create database if not exists chatRoom;

create table if not exists chatRoom.account(
    id varchar(10) primary key ,
    phone varchar(20) unique ,
    lastname varchar(25),
    firstname varchar(20)
    );

create table if not exists chatRoom.contacts(
    owner_id varchar(10),
    member_id varchar(10),
    foreign key (owner_id) references account(id) ON DELETE CASCADE,
    foreign key (member_id) references account(id) ON DELETE CASCADE,
    primary key (owner_id,member_id)
    );



create table if not exists chatRoom.groupinfo(
    g_id varchar(10) primary key ,
    creator_id varchar(10),
    create_date datetime,
    group_name varchar(10),
    member_num int,
    foreign key (creator_id) references account(id) ON DELETE CASCADE
    );

create table if not exists chatRoom.message(
    m_id int auto_increment primary key ,
    receiver_id varchar(10),
    sender_id varchar(10),
    group_id varchar(10),
    m_text varchar(200),
    send_time datetime,
    is_group int,
    foreign key (sender_id) references account(id) ON DELETE CASCADE,
    foreign key (group_id) references groupinfo(g_id) ON DELETE CASCADE,
    foreign key (receiver_id) references account(id) ON DELETE CASCADE
);


create table if not exists chatRoom.groupMembership(
    user_id varchar(10),
    g_id varchar(10),
    foreign key (user_id) references account(id) ON DELETE CASCADE,
    foreign key (g_id) references groupinfo(g_id) ON DELETE CASCADE,
    primary key (user_id,g_id)
    );

ALTER TABLE chatRoom.account ADD COLUMN joined_date datetime;
UPDATE chatRoom.account SET joined_date = NOW() WHERE joined_date is null;
ALTER TABLE chatRoom.account MODIFY COLUMN joined_date DATETIME DEFAULT CURRENT_TIMESTAMP;

######################################################################
#add index
#part2

ALTER TABLE chatRoom.account ADD UNIQUE ph (phone);
ALTER TABLE chatRoom.account ADD index fullname (firstname,lastname);
ALTER TABLE chatRoom.message ADD INDEX send (sender_id);
ALTER TABLE chatRoom.message ADD INDEX receive(receiver_id,group_id);
ALTER TABLE chatRoom.message ADD INDEX stmie(send_time);

######################################################################
#add view
#part3

CREATE VIEW user_message AS
    SELECT id,phone,firstname,lastname,joined_date,m_text from
    chatRoom.message m join chatRoom.account a on m.sender_id = a.id;
#SELECT * FROM user_message;

CREATE VIEW user_contacts AS
    SELECT user1.firstname as owner_name , user2.firstname as member_name
    FROM chatRoom.account user1 join chatroom.contacts c on user1.id = c.owner_id
    join chatroom.account user2 on c.member_id = user2.id;
#SELECT * FROM user_contacts;

CREATE VIEW user__messages__group AS
    SELECT u.firstname , g.group_name , m.m_text
    FROM chatRoom.account u join chatroom.groupMembership gm on u.id = gm.user_id
    join groupinfo g on gm.g_id = g.g_id
    left join chatroom.message m on m.sender_id = gm.user_id and m.is_group=1 and gm.g_id = m.group_id  ;
#SELECT * FROM user__messages__group;

######################################################################
#assertion ... -> trigger (mysql does not support assertion!)
#these checks are not necessary because the given field are unique
#part4

#check duplicate phone
DELIMITER //
CREATE trigger check_phone_unique1 before update on chatRoom.account
    for each row
    begin
        declare phone_cnt INT;
        SELECT COUNT(*) INTO phone_cnt
        FROM chatRoom.account WHERE phone = NEW.phone AND id != NEW.id;
        IF phone_cnt > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'duplicate phone';
            rollback ;
        end if;
    end;
//
DELIMITER ;

DELIMITER //
CREATE trigger check_phone_unique2 before insert on chatRoom.account
    for each row
begin
    declare phone_cnt INT;
    SELECT COUNT(*) INTO phone_cnt
    FROM chatRoom.account WHERE phone = NEW.phone ;
    IF phone_cnt > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'duplicate phone';
        rollback ;
    end if;
end;
//
DELIMITER ;

#check duplicate owner group
##you can update a group owner and it already has a unique owner because of the insert trigger and
#mind that there is just one record for each group

DELIMITER //
CREATE trigger check_group_owner_unique2 before insert on chatRoom.groupinfo
    for each row
begin
    declare owner_cnt INT;
    SELECT COUNT(*) INTO owner_cnt
    FROM chatRoom.groupinfo WHERE g_id = NEW.g_id ;
    IF owner_cnt > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'duplicate owner';
        rollback ;
    end if;
end;
//
DELIMITER ;
INSERT INTO groupinfo(g_id, creator_id) values ('@test','prndkh');
#INSERT INTO groupinfo(g_id, creator_id) values ('@test','kikish'); #error trigger tested


#####################################################################
#grant privileges
#part5

CREATE USER 'Arousha_Azad'@'%' IDENTIFIED BY 'Arousha2000azad';
GRANT SELECT,INSERT,DELETE,UPDATE ON chatRoom.* TO 'Arousha_Azad'@'%';
REVOKE INSERT,UPDATE,DELETE ON chatRoom.* FROM 'Arousha_Azad'@'%';
FLUSH PRIVILEGES ;
SHOW GRANTS FOR 'Arousha_Azad'@'%';

#####################################################################
#log table
#part 6
create table if not exists chatRoom.LOG(
    l_id int auto_increment primary key,
    table_name varchar(20),
    edit_time timestamp,
    edit_type varchar(10),
    userid varchar(10),
    record varchar(10),
    attribute varchar(10),
    check ( edit_type IN ('UPDATE','DELETE','INSERT'))
);

SET @current_user_id = 'ADMIN'; #this can be handled for each logged in user in front

#triggers for table account:
DELIMITER //
CREATE TRIGGER insert_account AFTER INSERT ON chatRoom.account
    FOR EACH ROW
    BEGIN
        INSERT INTO chatRoom.LOG (table_name, edit_time, edit_type, userid, record, attribute)
            VALUES('account', NOW() , 'INSERT', @current_user_id , NEW.id, NULL);
    end //
DELIMITER ;

DELIMITER //
CREATE TRIGGER delete_account AFTER DELETE ON chatRoom.account
    FOR EACH ROW
BEGIN
    INSERT INTO chatRoom.LOG (table_name, edit_time, edit_type, userid, record, attribute)
    VALUES('account', NOW() , 'DELETE', @current_user_id , OLD.id, NULL);
end //
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_account AFTER UPDATE ON chatRoom.account
    FOR EACH ROW
BEGIN
    IF NOT(NEW.id <=> OLD.id) THEN#CHECKS IF UPDATE IS ON ID OR NOT
        INSERT INTO chatRoom.LOG (table_name, edit_time, edit_type, userid, record, attribute)
        VALUES('account', NOW() , 'UPDATE', @current_user_id , OLD.id, 'id');
        end if;

    IF NOT(NEW.firstname <=> OLD.firstname) THEN
        INSERT INTO chatRoom.LOG (table_name, edit_time, edit_type, userid, record, attribute)
        VALUES('account', NOW() , 'UPDATE', @current_user_id , OLD.id, 'firstname');
    end if;

    IF NOT(NEW.lastname <=> OLD.lastname) THEN
        INSERT INTO chatRoom.LOG (table_name, edit_time, edit_type, userid, record, attribute)
        VALUES('account', NOW() , 'UPDATE', @current_user_id , OLD.id, 'lastname');
    end if;

    IF NOT(NEW.phone <=> OLD.phone) THEN
        INSERT INTO chatRoom.LOG (table_name, edit_time, edit_type, userid, record, attribute)
        VALUES('account', NOW() , 'UPDATE', @current_user_id , OLD.id, 'phone');
    end if;
end //
DELIMITER ;

#testing:
#INSERT INTO chatRoom.account (id, phone, lastname, firstname) VALUES ('@test2','11111111111','ttt','ttt');
#UPDATE chatRoom.account SET phone='2222222222' WHERE id = '@test2';
#DELETE FROM chatRoom.account WHERE id='@test2';

#####################################
#functions
#part7

CREATE FUNCTION count_messages_between_users(user1_id varchar(10),user2_id varchar(10))
    returns INT
    READS SQL DATA
    begin
        declare message_cnt INT;
         SELECT COUNT(*) INTO message_cnt
         FROM chatRoom.message
             WHERE (sender_id=user1_id AND receiver_id=user2_id AND is_group=0)
                    OR (sender_id=user2_id AND receiver_id=user1_id AND is_group=0);
        return message_cnt;
    end;

#test:
#SELECT count_messages_between_users('prndkh','kikish') AS total;
#INSERT INTO chatRoom.message (receiver_id, sender_id, group_id, m_text, send_time, is_group) VALUES
#            ('kikish','prndkh',NULL,'salame dobare',NOW(),0);

#INSERT INTO chatRoom.message (receiver_id, sender_id, group_id, m_text, send_time, is_group) VALUES
 #   ('kikish','prndkh',NULL,'alooo',NOW(),0);


CREATE PROCEDURE get_recent_active_user()
BEGIN
    SELECT sender_id,send_time
    FROM chatRoom.message
    WHERE send_time>=now()- interval 24 hour
    ORDER BY send_time DESC ;
end;

#test:
#CALL get_recent_active_user();


CREATE PROCEDURE get_conversation_history(IN user1_id varchar(10),IN user2_id varchar(10),IN limit_message int)
    BEGIN
        SELECT sender_id,receiver_id,m_text,send_time
            FROM chatRoom.message
                WHERE
                    (sender_id=user1_id AND receiver_id=user2_id AND is_group=0)
                OR (sender_id=user2_id AND receiver_id=user1_id AND is_group=0)
            ORDER BY send_time DESC LIMIT limit_message;
    end;
#test:
CALL get_conversation_history('kikish','prndkh',3);

CREATE PROCEDURE search_message(IN word varchar(30))
    BEGIN
        SELECT sender_id,receiver_id,group_id,m_text,send_time
            FROM chatRoom.message
                WHERE m_text LIKE CONCAT('%',word,'%')
            ORDER BY send_time DESC ;
    end;
#test
#CALL search_message('parand');

######################################
# هر کاربر )با اطالعات کامل( در چه گروههایی عضو است.
SELECT a.id AS account_id ,
       a.phone ,
       a.firstname ,
       a.lastname ,
       g.g_id AS group_id ,
       g.group_name ,
       g.create_date,
       g.creator_id
FROM chatRoom.account a
LEFT JOIN chatRoom.groupMembership gm ON a.id = gm.user_id
LEFT JOIN chatroom.groupinfo g ON gm.g_id = g.g_id;


#کاربران یک گروه )با اطالعات کامل( به ترتیب تعداد پیام های ارسال شده در آن گروه
SELECT a.id AS account_id,
       a.phone,
       a.firstname,
       a.lastname,
       COUNT(m.m_id) AS message_count
FROM chatRoom.groupMembership gm
LEFT JOIN chatRoom.message m ON  gm.user_id = m.sender_id AND gm.g_id = m.group_id
JOIN chatRoom.account a ON gm.user_id = a.id
WHERE gm.g_id = '@ceAut'
GROUP BY a.id
ORDER BY message_count DESC;


# هر گروه )با اطالعات کامل( چه تعداد کاربر دارد که با یکدیگر چت خصوصی دارند
SELECT g.g_id AS group_id ,
       g.group_name,
       g.creator_id,
       g.create_date,
       g.member_num,
       count(distinct gm.user_id) AS member_chat
FROM chatRoom.groupinfo g
JOIN chatRoom.groupMembership gm ON g.g_id = gm.g_id
LEFT JOIN chatRoom.message m1 ON m1.sender_id = gm.user_id AND m1.is_group = 0 AND m1.receiver_id IN(
    SELECT x.user_id FROM chatRoom.groupMembership x WHERE x.g_id = g.g_id
    )
LEFT JOIN chatRoom.message m2 ON m2.receiver_id = gm.user_id AND m2.is_group = 0 AND m2.sender_id IN(
    SELECT y.user_id FROM chatRoom.groupMembership y WHERE y.g_id = g.g_id
    )
WHERE m1.m_id is not null OR m2.m_id is not null
GROUP BY g.g_id;


# کاربرهایی که در یک روز بهخصوص وارد پیامرسان ما شده اند و داخل حداقل ۲ گروه بیشتر ازیک پیام را ارسال کرده اند

SELECT a.id,COUNT(distinct gm.g_id), count(distinct m.m_id)
FROM chatRoom.account AS a
INNER JOIN chatRoom.groupMembership gm ON a.id = gm.user_id
INNER JOIN chatRoom.message m ON m.is_group=1 AND  m.sender_id = gm.user_id AND gm.g_id = m.group_id
GROUP BY  a.id
HAVING COUNT(distinct gm.g_id) > 1 and count(distinct m.m_id) > 1
AND  a.id IN(
          SELECT b.id FROM chatRoom.account b WHERE b.joined_date ='2024-06-03 18:17:07'
      ) ;


#کاربرانی )با اطالعات کامل( که در یک یا چند گروه با یک کاربر خاص مشترک هستند.
SELECT * FROM chatRoom.account WHERE id IN(
SELECT gm2.user_id
FROM chatRoom.groupMembership gm
INNER JOIN chatRoom.groupMembership gm2 ON gm.g_id = gm2.g_id
WHERE gm.user_id = 'prndkh' AND gm2.user_id != 'prndkh');

