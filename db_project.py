import mysql.connector
from datetime import date



db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="prnd12AUT@",
    database="chatRoom",
    auth_plugin='mysql_native_password'
)

mycursor = db.cursor()



def operation(op, *args):
    try:
        op(mycursor,*args)
    except mysql.connector.Error as e:
        print(f"ERROR {e}")
        db.rollback()
    #finally:
    #   mycursor.close()
    #  db.close()        

#account
def insert_account(mycursor,id,phone,lastname,firstname):
    mycursor.execute(
        "INSERT INTO account(id,phone,lastname,firstname,joined_date) VALUES (%s,%s,%s,%s,%s)",(id,phone,lastname,firstname,date.today())
    )
    db.commit()
    if mycursor.rowcount != 0:
          print(f"account {id} is successfully added")
    else :
          print("an error has been occured")
                        

def read_account(mycursor,id):
        mycursor.execute(
             "SELECT * FROM account WHERE id = %s ",(id,) )
        res = mycursor.fetchall()
        print(res)
        
def update_account(mycursor,id,attribute,new):
     query = f"UPDATE account SET {attribute} = %s WHERE id = %s"
     mycursor.execute(query,(new,id))
     db.commit()
     if mycursor.rowcount != 0:
          print(f"account {id} is successfully updated")
     else :
          print("an error has been occured")              

def delete_account(mycursor,id):
     mycursor.execute(
        "DELETE FROM account WHERE id = %s",(id,))
     db.commit()
     if mycursor.rowcount != 0 :
        print(f"{id} is deleted")
     else :
        print("account not found")    
        
#contact
def insert_contacts(mycursor,owner_id,member_id):
    mycursor.execute(
        "INSERT INTO contacts(owner_id,member_id) VALUES (%s,%s)",(owner_id,member_id)
    )
    db.commit()    

def read_contacts(mycursor,owner_id):
     mycursor.execute("SELECT member_id FROM contacts WHERE owner_id = %s",(owner_id,))
     res = mycursor.fetchall()
     print(res)

def delete_contact(mycursor,owner_id,member_id):
      mycursor.execute(
        "DELETE FROM contacts WHERE owner_id = %s AND member_id = %s",(owner_id,member_id))
      db.commit()
      if mycursor.rowcount != 0 :
        print(f"{member_id} is deleted")
      else :
        print("account not found")     


#groupinfo
def insert_groupinfo(mycursor,g_id,creator_id,create_date,group_name):
    mycursor.execute(
        "INSERT INTO groupinfo(g_id,creator_id,create_date,group_name,member_num) VALUES (%s,%s,%s,%s,%s)",
        (g_id,creator_id,create_date,group_name,0)
    )
    db.commit() 

def read_groupinfo(mycursor,g_id):
     mycursor.execute("SELECT * FROM groupinfo WHERE g_id = %s",(g_id,))
     res = mycursor.fetchall()
     print(res)

def update_groupname(mycursor,user_id,g_id,new):
     mycursor.execute("SELECT creator_id FROM groupinfo WHERE g_id = %s",(g_id,))
     id = mycursor.fetchone()
     print(id)
     if id and id[0]== user_id :
          mycursor.execute("UPDATE groupinfo SET group_name = %s WHERE g_id = %s",(new,g_id))
          db.commit()
     else : 
          print ("not allowed")
     if mycursor.rowcount != 0 :
        print(f"groupname is successfully updated to {new}")
     else :
        print("an error has been occured")


def update_group_member_num(mycursor,g_id,op):
    mycursor.execute("SELECT member_num FROM groupinfo WHERE g_id = %s",(g_id,))
    old = mycursor.fetchone()
    if old and op=="++":
        new = old[0]+1
    elif old and old[0]>0 and op =="--":
        new = old[0]-1
    else:
        print("invalid action")
        return
            
    mycursor.execute("UPDATE groupinfo SET member_num = %s WHERE g_id =%s",(new,g_id))
    db.commit()         

    if mycursor.rowcount != 0 :
        print(f"member num is successfully updated to {new}")
    else :
        print("an error has been occured")
     
   

def delete_group(mycursor,creator_id,parameter,value):
    mycursor.execute(f"DELETE FROM groupinfo WHERE creator_id = %s AND {parameter} = %s",(creator_id,value))
    db.commit()
    if mycursor.rowcount != 0 :
        print("group is deleted")
    else :#1-user is not allowed to delete the group 2-group not found
        print("an error has been occured")
        


#message
def insert_message(mycursor,receiver_id,sender_id,group_id,m_text,send_time,is_group):
    mycursor.execute(
        "INSERT INTO message(receiver_id,sender_id,group_id,m_text,send_time,is_group) VALUES (%s,%s,%s,%s,%s,%s)",
        (receiver_id,sender_id,group_id,m_text,send_time,is_group)
    )
    db.commit()      

def read_message_chat(mycursor,sener_id,receiver_id):
     mycursor.execute("SELECT * FROM message WHERE receiver_id = %s AND sender_id = %s",(receiver_id,sener_id))
     res = mycursor.fetchall()
     print(res)  

def read_message_group(mycursor,g_id):
     mycursor.execute("SELECT * FROM message WHERE group_id = %s",(g_id,))
     res = mycursor.fetchall()
     print(res)

def update_message(mycursor,user_id,m_id,new):
     mycursor.execute("SELECT sender_id FROM message WHERE m_id = %s",(m_id,))
     id = mycursor.fetchone()
     if id and id[0] == user_id :
          mycursor.execute("UPDATE message SET m_text = %s WHERE m_id = %s",(new,m_id))
          db.commit()
          if mycursor.rowcount != 0 :
            print("done!")
          else :
            print("an error has been occured")
     else : 
           print("not allowed")
     
def delete_message(mycursor,user_id,m_id):
    mycursor.execute("SELECT sender_id FROM message WHERE m_id = %s",(m_id,))
    id = mycursor.fetchone()
    if id and id[0] == user_id :
          mycursor.execute("DELETE FROM message WHERE m_id = %s",(m_id,))
          db.commit()
          if mycursor.rowcount != 0 :
            print("done!")
          else :
            print("an error has been occured")
    else : 
          print("not allowed")    

#groupMembership
def insert_groupMembership(mycursor,user_id,g_id):
    mycursor.execute(
        "INSERT INTO groupMembership(user_id,g_id) VALUES (%s,%s)",(user_id,g_id)
    )
    db.commit()
    print(f"{user_id} joined {g_id}")
    update_group_member_num(mycursor,g_id,"++")
    

def read_group_users(mycursor,g_id):
     mycursor.execute("SELECT user_id FROM groupMembership WHERE g_id = %s",(g_id,))
     res = mycursor.fetchall()
     print(res)    

def read_user_groups(mycursor,user_id):
     mycursor.execute("SELECT g_id FROM groupMembership WHERE user_id = %s",(user_id,))
     res = mycursor.fetchall()
     print(res)

def leave_gruop(mycursor,user_id,g_id):
    mycursor.execute("DELETE FROM groupmembership WHERE user_id = %s AND g_id = %s",(user_id,g_id))
    db.commit()
    if mycursor.rowcount != 0:
          mycursor.execute("SELECT group_name FROM groupinfo WHERE g_id = %s",(g_id,))
          name = mycursor.fetchone()
          print(f"you left {name[0]} at {date.today()}")
          update_group_member_num(mycursor,g_id,"--")
    else :
          print("an error has been occured")


#doc testcase:##########################################################
########################################################################

#insert_account("Tom_kane","44796268462","Kane","Tom")
#operation(insert_message,"prndkh","Tom_kane",None,"hi",date.today(),0)
#operation(insert_groupMembership,"Tom_kane","@uni")
#update_account("Tom_kane","phone","44734278080")

########################################################################

mycursor.execute("SELECT id FROM account WHERE id NOT IN(SELECT user_id FROM groupmembership)")
res = mycursor.fetchall()
delete = [row[0] for row in res]
#print(res)
#print(delete)
for i in delete:
    operation(delete_account,i)

#########################################################################
#menu:###################################################################
print("""
what do you want to do?
      1.create account
      2.update account
      3.see profile
      4.delete account
      5.add contact
      6.see contacts
      7.delete contact
      8.add group
      9.see group information
      10.change group name
      11.delete group
      12.send a message in pv
      13.send a message in a group
      14.read chat messages
      15.read group messages
      16.edit a message
      17.delete a message
      18.add group member
      19.see all group members
      20.see all groups of a user
      21.leave a group
""")

op = int(input("enter your choice: "))

if op == 1: #id,phone,lastname,firstname
    id = input("id: ")
    phone = input("phone: ")
    firstname = input("firstname: ")
    lastname = input("lastname: ")
    operation(insert_account,id,phone,lastname,firstname)

elif op == 2 :#id,attribute,new
    id = input("id: ")
    attribute = input("what do you waant to change?")
    new = input("write your new value: ")
    operation(update_account,id,attribute,new)

elif op == 3: #id
    id = input("id: ")
    operation(read_account,id)

elif op == 4 : #id
    id = input("id: ")
    operation(delete_account,id)

elif op == 5 : #owner_id,member_id 
    id = input("your id: ")
    member = input("who do you want to add ? :")
    operation(insert_contacts,id,member)

elif op == 6: #id
    id = input("id: ")
    operation(read_contacts,id)

elif op == 7:#owner_id,member_id 
    id = input("your id: ")
    member = input("who do you want to remove ? :")
    operation(delete_contact,id,member)  

elif op == 8:#g_id,creator_id,create_date,group_name
    g_id = input("group id: ")
    creator = input("your id: ")
    name = input("group name: ")
    operation(insert_groupinfo,g_id,creator,date.today(),name)

elif op == 9: #g_id
    id = input("group id: ")
    operation(read_groupinfo,id)

elif op == 10: #user_id,g_id,new
    user = input("your id : ")
    gid = input("group id: ")
    new = input("new name : ")
    operation(update_groupname,user,gid,new)

elif op == 11 :#creator_id,parameter,value
    creator = input("your id: ")
    print("which groups would you like to delete?")
    parameter = input("field: ")
    value = input("that has value of: ")
    operation(delete_group,creator,parameter,value)

elif op == 12 :#receiver_id,sender_id,group_id,m_text,send_time,is_group)
    receiver = input("who would you like to text? ")
    sender = input("your id: ")
    text = input("write your message: ")
    operation(insert_message,receiver,sender,None,text,date.today,0)

elif op == 13 :#,receiver_id,sender_id,group_id,m_text,send_time,is_group)    
    g = input("to which group would you like to text? ")
    sender = input("your id: ")
    text = input("write your message: ")
    operation(insert_message,None,sender,g,text,date.today,1)

elif op == 14  :#,sener_id,receiver_id
    print("what chat do you want to read? ")
    sender = input("sender: ")
    receiver = input("receiver: ")
    operation(read_message_chat,sender,receiver)

elif op == 15: #,g_id
    print(" what group do you like to read ?")
    g = input("group id: ")
    operation(read_message_group,g)

elif op == 16 :#,user_id,m_id,new
    id = input("your id: ")
    m = input("what message would you like to edit? : ")
    new = input("edited text: ")
    operation(update_message,id,m,new)

elif op == 17 :#user_id,m_id
    id = input("your id: ")
    m = input("what text? :")
    operation(delete_message,id,m)

elif op == 18: #user_id,g_id
    id = input("who do you want to add? ")
    g = input("to what group?: ")
    operation(insert_groupMembership,id,g)

elif op == 19 :#g_id
    g = input("which group members do you want to see? :")
    operation(read_group_users,g)

elif op == 20: #user_id
    id = input("what user groups would you like to see? :")
    operation(read_user_groups,id)

elif op == 21 :#user_id,g_id
    id = input("id : ")
    g = input("leave which group? : ")
    operation(leave_gruop,id,g)


#my samples:#############################################################

#insert_account("prndkh","09021382924","khalili","parand")  
#insert_account("kikish","09129796935","sherafati","kiana")
#insert_account("goli","09126666935","golmamadi","narges")
#insert_account("pg","09129123435","poorghasemi","parsa")
#insert_account("nasimimi","09129788835","koohestani","nasim")
#insert_account("nofa","09111796935","fathi","ariyan")
#insert_account("ghr","09129000935","gahremani","koorosh")
#insert_account("bita","09012138292","zhian","kiana")
#insert_account("anna","09139796935","motaghi","armina")
#insert_account("fayyaz","09129799935","fayyaz","mohammad")

#operation(insert_groupinfo,"@ceAut","prndkh", date.today(),"ce")
#operation(insert_groupMembership,"kikish","@ceAut")
#operation(insert_groupMembership,"anna","@ceAut")
#operation(insert_groupMembership,"prndkh","@ceAut")
#operation(insert_groupMembership,"fayyaz","@ceAut")
#operation(delete_group,"kikish","g_id","@uni")

#operation(insert_groupinfo,"@uni","kikish",date.today(),"friends:)")
#operation(insert_groupMembership,"prndkh","@uni")
#operation(insert_groupMembership,"kikish","@uni")
#operation(insert_groupMembership,"goli","@uni")

#operation(insert_contacts,"prndkh","kikish")
#operation(insert_contacts,"prndkh","goli")
#operation(insert_contacts,"prndkh","pg")
#operation(insert_contacts,"prndkh","nasimimi")
#operation(insert_contacts,"prndkh","anna")

#operation(insert_contacts,"kikish","prndkh")
#operation(insert_contacts,"kikish","goli")
#operation(insert_contacts,"kikish","anna")
#operation(insert_contacts,"kikish","pg")
#operation(insert_contacts,"kikish","nasimimi")

#operation(insert_message,None,"prndkh","@ceAut","salam bache ha",date.today(),1)
#operation(insert_message,None,"kikish","@ceAut","salam khobi",date.today(),1)
#operation(insert_message,None,"prndkh","@ceAut","qurbunet",date.today(),1)
#operation(insert_message,None,"anna","@ceAut","salammm",date.today(),1)
#operation(insert_message,None,"prndkh","@uni","kasi hast????",date.today(),1)

#operation(insert_message,"kikish","prndkh",None,"salam parand",date.today(),0)
#operation(insert_message,"prndkh","kikish",None,"salam chetori",date.today(),0)

#print(read_user_groups("prndkh"))
#print(read_contacts("prndkh"))
#update_account("prndkh","firstname","parandehee")
#delete_account("bita")
#leave_gruop("fayyaz","@ceAut")
#insert_groupMembership("nasimimi","@ceAut")
#insert_groupMembership("fayyaz","@ceAut")
#leave_gruop("nasimimi","@ceAut")
#leave_gruop("fayyaz","@ceAut")
#insert_account("sos","11111111111","sos",'sos')
#delete_account("sos")
#leave_gruop("nasimimi","@ceAut")
#update_groupname("prndkh","@ceAut","cecesos")
#delete_contact("prndkh","anna")
#read_groupinfo("@ceAut")
#update_groupname("prndkh","@ceAut","ce")
#update_group_member_num("@ceAut","--")
#update_message("prndkh",1,"salam bache ha <3")  
#insert_message(None,"prndkh","@ceAut","fjfdjfjk",date.today(),1)     
#delete_message("prndkh",8)
#leave_gruop("fayyaz","@ceAut")
#insert_groupMembership("fayyaz","@ceAut")


#operation(insert_message,None,"prndkh","@ceAut","helppp",date.today(),1)
#operation(insert_message,None,"kikish","@ceAut","what?",date.today(),1)
#operation(insert_message,None,"prndkh","@ceAut","nothing",date.today(),1)
#operation(insert_message,"prndkh","fayyaz",None,"sos",date.today(),0)
#operation(insert_account,"ssmk","99979969999","n","k")
#operation(insert_groupMembership,"id","@ceAut")
#operation(delete_account,"id")
#operation(insert_contacts,"prndkh","id")

#operation(update_account,"goli","joined_date","2024-04-03 18:17:07")
#operation(update_account,"kikish","joined_date","2023-04-03 18:17:07")
#operation(insert_message,"prndkh","anna",None,"salam salam",date.today(),0)
#operation(insert_account,"soodi","44790008462","soodi","soodi")
#operation(insert_message,"soodi","prndkh",None,"salam ....salam",date.today(),0)
#operation(read_account,"prndkh")
#operation(update_account,"prndkh","firstname","Parand")





