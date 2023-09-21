from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.db import connection
import pypyodbc
import json
import datetime
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import pandas as pd
import os
import pypyodbc
import bcrypt
import base64
from .imp_info import DATABASE_UID, DATABASE_PWD,DB_SERVER,DB_NAME
from django.http import HttpResponse,FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import qrcode
from pathlib import Path
import io
import shutil
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from xlsxwriter.workbook import Workbook
import logging
from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
logging.debug(BASE_DIR)
def encode_password(plain_password):
    hashed_password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())
    return hashed_password.decode()
def connect_to_db():
    conn = pypyodbc.connect(
            'Driver={SQL Server};'
            f'Server={DB_SERVER};'
            f'Database={DB_NAME};'
            f'uid={DATABASE_UID};'
            f'pwd={DATABASE_PWD}'
        )

    cursor = conn.cursor()
    return cursor,conn
def fetch_item_qty(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        data=json.loads(request.body)
        item=data.get('item_id')
        query=f"select qty from item where qr_id=?"
        value=(item,)
        cursor.execute(query,value)
        qty=cursor.fetchone()
        return JsonResponse({'qty':qty}, status=200)
def edit_category(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        data=json.loads(request.body)
        category_name=data.get('category')
        new_category=data.get('new_category')
        logging.debug(category_name,new_category)
        select_query = f"SELECT * FROM category WHERE  category_name=?"
        select_values = (new_category,)
        cursor.execute(select_query, select_values)
        category_data = cursor.fetchall()
        if len(category_data)>0:
            cursor.close()
            conn.close()
            return JsonResponse({'success': 'Category already exists Kindly give another name'}, status=200)
        else:
            query=f"UPDATE category set category_name=? where category_name=?"
            values=(new_category,category_name)
            cursor.execute(query,values)
            conn.commit()
            return JsonResponse({'success': 'Category Name has been updated successfully'}, status=200)
def check_inventory(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        qrid=request.POST['qrid']
        qty=request.POST['qty']
        query="""select qty from item where qr_id=?"""
        values=(qrid,)
        cursor.execute(query, values)
        actual_qty=cursor.fetchone()
        if actual_qty[0]>=int(qty):  
            return JsonResponse({'success': "Inventory Available"}, status=200)
        else:
            return JsonResponse({'success': "Inventory Not Available"}, status=200)
def issue_stock_view(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        category=request.POST['category']
        item=request.POST['item']
        query="""Select item_name from item where qr_id=?"""
        values=(item,)
        cursor.execute(query,values)
        item_name=cursor.fetchone()
        item_name=item_name[0]
        query="""Select category_name from category where category_id=?"""
        values=(category,)
        cursor.execute(query,values)
        category_name=cursor.fetchone()
        category_name=category_name[0]
        qty=request.POST['qty']
        
        print(category,item,qty)
        query="""select qty from item where qr_id=?"""
        values=(item,)
        cursor.execute(query, values)
        actual_qty=cursor.fetchone()
        if actual_qty[0]>=int(qty):  
            return JsonResponse({'success': "Inventory Available", 'qty':qty,'category':category_name,'item':item_name,'qrid':item}, status=200)
        else:
            return JsonResponse({'success': "Inventory Not Available"}, status=200)

    
def receive_stock_view(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        category=request.POST['category']
        item=request.POST['item']
        query="""Select item_name from item where qr_id=?"""
        values=(item,)
        cursor.execute(query,values)
        item_name=cursor.fetchone()
        item_name=item_name[0]
        query="""Select category_name from category where category_id=?"""
        values=(category,)
        cursor.execute(query,values)
        category_name=cursor.fetchone()
        category_name=category_name[0]
        qty=request.POST['qty']
        vendor=request.POST['vendor']
        del_partner=request.POST['del_partner']
        # if request.POST['photo']=="undefined":
        #     photo=""
        #     photo_extension=""
        # else:
        #     photo=request.FILES['photo']
        #     photo_extension = photo.name.split('.')[-1]
        if request.POST['order']=="undefined":
            order=""
            order_extension=""
        else:
            order=request.FILES['order']
            order_extension = order.name.split('.')[-1]
        remarks=request.POST['remarks']
        print(category,item,qty,order_extension,order,remarks)
        insert_query="""INSERT INTO receive_stock (category_id,qr_id,qty,vendor,deliv_partner,remarks) VALUES(?,?,?,?,?,?)"""
        insert_values=(category,item,qty,vendor,del_partner,remarks,)
        cursor.execute(insert_query, insert_values)
        conn.commit()
        update_query="""UPDATE item SET qty=? where qr_id=?"""
        update_values=(qty,item,)
        cursor.execute(update_query,update_values)
        conn.commit() 
        query="""SELECT TOP(1) id from receive_stock order by dated desc"""
        cursor.execute(query)
        id=cursor.fetchone()
        id=id[0]
        # if photo!="":
        #     with open(str(BASE_DIR)+'\\mysite\\static\\pdfs\\Photo\\C' + str(category) +"I"+str(item)  + str(id) +'.' + photo_extension, 'wb+') as destination:
        #         for chunk in photo.chunks():
        #             destination.write(chunk)
        if order!="":
            with open(str(BASE_DIR)+'\\mysite\\static\\pdfs\\PurchaseOrder\\C' + str(category) +"I"+str(item)  + str(id) +'.' + order_extension, 'wb+') as destination:
                for chunk in order.chunks():
                    destination.write(chunk)
        qr_code_data = {'Item name': item_name, 'QR ID': item,'Category':category_name,'Qty':qty}
        qr_code_size = 25  # Adjust the size as per your requirement

        qr_image = generate_qr_code(qr_code_data, qr_code_size)
        # Save the QR code image
        file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
        qr_code_filename = file_path+ f"{item}.png"
        logging.debug(qr_image.width,qr_image.height)
        qr_image.save(qr_code_filename)
        return JsonResponse({'success': 'Request ID '+ str(id)+' Created successfully'}, status=200)
 
def request_stock_view(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        category=request.POST['category']
        item=request.POST['item']
        qty=request.POST['qty']
        order=request.FILES['order']
        order_extension = order.name.split('.')[-1]
        remarks=request.POST['remarks']
        print(category,item,qty,order_extension,order,remarks)
        insert_query="""INSERT INTO request_stock (category_id,qr_id,qty,remarks) VALUES(?,?,?,?)"""
        insert_values=(category,item,qty,remarks,)
        cursor.execute(insert_query, insert_values)
        conn.commit()
        query="""SELECT TOP(1) id from request_stock order by dated desc"""
        cursor.execute(query)
        id=cursor.fetchone()
        id=id[0]
        with open(str(BASE_DIR)+'\\mysite\\static\\pdfs\\RequestOrder\\RC' + str(category) +"I"+str(item)  + str(id) +'.' + order_extension, 'wb+') as destination:
            for chunk in order.chunks():
                destination.write(chunk)
        return JsonResponse({'success': 'Request ID '+ str(id)+' Created successfully'}, status=200)
            
def delete_item(request):
    data=json.loads(request.body)
    cursor,conn=connect_to_db()
    item=data.get('item')

    query=f"SELECT status from item where qr_id=?"
    value=(item,)
    cursor.execute(query,value)
    status=cursor.fetchone()
    status=status[0]
    if status=='AVAILABLE':
        query=f" select qr_id,item_name,category_id,type from item where qr_id=?"
        value=(item,)
        cursor.execute(query,value)
        data=cursor.fetchone()
        query=f" INSERT INTO deleted_items (qr_id,item_name,category_id,type) VALUES(?,?,?,?)"
        value=(data[0],data[1],data[2],data[3])
        cursor.execute(query,value)
        conn.commit()
        query=f" DELETE from item where qr_id=?"
        value=(item,)
        cursor.execute(query,value)
        conn.commit()
        query=f" DELETE from weapon_assign where qr_id=?"
        value=(item,)
        cursor.execute(query,value)
        conn.commit()
        query=f" DELETE from inventory_data where qr_id=?"
        value=(item,)
        cursor.execute(query,value)
        conn.commit()
        return JsonResponse({'success':'Item has been successfully Deleted'}, status=200)
    else:
        return JsonResponse({'success':'Item is Currently Issued. Issued Items cannot be deleted'}, status=200)
def modify_qty(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        data=json.loads(request.body)
        item=data.get('item_id')
        new_qty=int(data.get('newqty'))
        actual_qty=int(data.get('actualqty'))
        category_id=int(data.get('category_id'))
        userid=request.session.get('empid')
        query=f"UPDATE item set qty=? where qr_id=?"
        values=(actual_qty+new_qty,item,)
        cursor.execute(query,values)
        conn.commit()
        query=f"INSERT into inventory_audit (category_id,qr_id,qty,action,userid) VALUES(?,?,?,?,?)"
        if new_qty>0:
            values=(category_id,item,new_qty,'ADDED',userid,)
        else:
            values=(category_id,item,-(new_qty),'REMOVED',userid,)
        cursor.execute(query,values)
        conn.commit()
        cursor.close()
        conn.close()
        return JsonResponse({'success': 'Item Quantity has been updated successfully'}, status=200)
def edit_qr(request):
    if request.method == 'POST':
        cursor,conn=connect_to_db()
        data=json.loads(request.body)
        item_name=data.get('item')
        new_item=data.get('new_item')
        logging.debug(item_name,new_item)
        select_query = f"SELECT * FROM item WHERE  item_name=?"
        select_values = (new_item,)
        cursor.execute(select_query, select_values)
        item_data = cursor.fetchall()
        if len(item_data)>0:
            return JsonResponse({'success': 'Item already exists. Give Another Name'}, status=200)
        else:
            query=f"UPDATE item set item_name=? where item_name=?"
            values=(new_item,item_name,)
            cursor.execute(query,values)
            conn.commit()
            query=f"select qr_id from item where item_name=?"
            values=(new_item,)
            cursor.execute(query,values)
            qr_id=cursor.fetchone()
            qr_id=qr_id[0]
            cursor.close()
            conn.close()
            qr_code_data = {'Item name': new_item, 'QR ID': qr_id}
            qr_code_size = 25  # Adjust the size as per your requirement

            qr_image = generate_qr_code(qr_code_data, qr_code_size)
            # Save the QR code image
            file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
            qr_code_filename = file_path+ f"{qr_id}.png"
            logging.debug(qr_image.width,qr_image.height)
            qr_image.save(qr_code_filename)
            return JsonResponse({'success': 'Item Name has been updated successfully'}, status=200)
def get_items(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category_id = data.get('category')
        logging.debug(category_id)
        cursor,conn=connect_to_db()
        query = "SELECT qr_id, item_name FROM item WHERE category_id = ?"
        cursor.execute(query, (category_id,))
        items = cursor.fetchall()
        logging.debug(items)
        cursor.close()
        conn.close()
        if items:
            items_data = [{'qr_id': item[0], 'item_name': item[1]} for item in items]
            return JsonResponse(items_data, safe=False)
        else:
            return JsonResponse({'error': 'No items found for the selected category'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
def generate_pdf_qr_receive(request):
    data=json.loads(request.body)
    cursor,conn=connect_to_db()
    position=data.get('position')
    item=data.get('item')
    query=f"select item_name from item where qr_id=?"
    values=(item,)
    cursor.execute(query,values)
    item_name=cursor.fetchone()
    item_name=item_name[0]
    file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
    qr_code_filename = file_path+ f"{item}.png"
    logging.debug(position,item_name,qr_code_filename,item)
    doc = FPDF()

    block_width = 70  # Block width in mm
    block_height = 46 # Block height in mm
    block_margin = 2  # Block margin in mm
    doc.add_page()
    # for i in range(1,19):
        # Calculate the x and y coordinates based on the selected position
    selected_block = int(position)
    blocks_per_row = 3  # Number of blocks per row
    x = ((selected_block - 1) % blocks_per_row) * (block_width + block_margin)
    y = 5 + ((selected_block - 1) // blocks_per_row) * (block_height + block_margin)

        # Add the QR code image to the PDF at the specified position
    doc.image(qr_code_filename, x, y, block_width, block_height)
    logging.debug(x,y)
        # Add the entered text above the QR code
    doc.set_font("Arial", 'B',size=8)
    doc.text(x+10, y+2 , str(item))
    doc.text(x+35, y+2 , item_name)

    save_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\QR_Code.pdf"
    # Save the PDF with a unique filename
    doc.output(save_path)
    cursor.close()
    conn.close()
    return JsonResponse({'success':'Item with QR ID '+ str(item) + ' has been added to Inventory'}, status=200)

def generate_pdf_with_qr_codes(request):
    data=json.loads(request.body)
    cursor,conn=connect_to_db()
    position=data.get('position')
    item_name=data.get('item_name')
    query=f"select qr_id from item where item_name=?"
    values=(item_name,)
    cursor.execute(query,values)
    qr_id=cursor.fetchone()
    qr_id=qr_id[0]
    file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
    qr_code_filename = file_path+ f"{qr_id}.png"
    logging.debug(position,item_name,qr_code_filename,qr_id)
    doc = FPDF()

    block_width = 70  # Block width in mm
    block_height = 46 # Block height in mm
    block_margin = 2  # Block margin in mm
    doc.add_page()
    # for i in range(1,19):
        # Calculate the x and y coordinates based on the selected position
    selected_block = int(position)
    blocks_per_row = 3  # Number of blocks per row
    x = ((selected_block - 1) % blocks_per_row) * (block_width + block_margin)
    y = 5 + ((selected_block - 1) // blocks_per_row) * (block_height + block_margin)

        # Add the QR code image to the PDF at the specified position
    doc.image(qr_code_filename, x, y, block_width, block_height)
    logging.debug(x,y)
        # Add the entered text above the QR code
    doc.set_font("Arial", 'B',size=8)
    doc.text(x+10, y+2 , str(qr_id))
    doc.text(x+35, y+2 , item_name)

    save_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\QR_Code.pdf"
    # Save the PDF with a unique filename
    doc.output(save_path)
    cursor.close()
    conn.close()
    return JsonResponse({'success':'Item with QR ID '+ str(qr_id) + ' has been added to Inventory'}, status=200)
@login_required
def qr_code(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    cat=fetch_category()
    category_dict = dict(cat)
    context = {'categories':category_dict,'username': username, 'location': location,'empid':empid}
    return render(request,'qr_code.html',context)
def generate_qr_code(data, size):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size // 65,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    return qr_image
def add_item_view(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        category_name=data.get('category_name')
        item_name=data.get('item_name')
        weapon_type=data.get('type')
        # qty=data.get('qty')
        table_name='item'
        cursor,conn=connect_to_db()
        select_query=f"SELECT category_id from category where category_name=?"
        select_values=(category_name,)
        cursor.execute(select_query,select_values)
        category_id=cursor.fetchone()
        category_id=category_id[0]
        select_query = f"SELECT * FROM item WHERE  item_name=?"
        select_values = (item_name,)
        cursor.execute(select_query, select_values)
        item_data = cursor.fetchall()
        if len(item_data)>0:
            cursor.close()
            conn.close()
            return JsonResponse({'success': 'Item already exists'}, status=200)
        else:
            insert_query = f"INSERT INTO {table_name} (item_name,category_id,status,assigned_status,type,qty) VALUES (?,?,?,?,?,?)"
            insert_values = (item_name,category_id,"AVAILABLE","N",weapon_type,1)
            cursor.execute(insert_query, insert_values)
            conn.commit()
            query=f"select id from {table_name} where category_id=? AND item_name=?"
            values=(category_id,item_name)
            cursor.execute(query,values)
            itemid=cursor.fetchone()
            itemid=itemid[0]
            query=f"UPDATE item set qr_id=? where id=?"
            values=(itemid,itemid)
            cursor.execute(query,values)
            conn.commit()
            query=f"select qr_id from item where item_name=?"
            values=(item_name,)
            cursor.execute(query,values)
            qr_id=cursor.fetchone()
            qr_id=qr_id[0]
            select_query = f"SELECT count(*) FROM inventory_data WHERE qr_id = ? AND category_id = ?"
            select_values = (qr_id,category_id)
            cursor.execute(select_query, select_values)
            inv_data=cursor.fetchone()
            logging.debug("count is " + str(inv_data[0]))
            if inv_data[0]==0:
                insert_query = f"INSERT INTO inventory_data (qr_id,category_id,type) VALUES (?,?,?)"
                insert_values = (qr_id,category_id,weapon_type)
                cursor.execute(insert_query, insert_values)
                conn.commit()
            cursor.close()
            conn.close()
            return JsonResponse({'success':"Item added Successfully"},safe=False)
        
def generate_qr_code_view(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        category_name=data.get('category_name')
        item_name=data.get('item_name')
        weapon_type=data.get('type')
        qty=data.get('qty')
        table_name='item'
        cursor,conn=connect_to_db()
        select_query=f"SELECT category_id from category where category_name=?"
        select_values=(category_name,)
        cursor.execute(select_query,select_values)
        category_id=cursor.fetchone()
        category_id=category_id[0]
        select_query = f"SELECT * FROM item WHERE  item_name=?"
        select_values = (item_name,)
        cursor.execute(select_query, select_values)
        item_data = cursor.fetchall()
        if len(item_data)>0:
            cursor.close()
            conn.close()
            return JsonResponse({'success': 'Item already exists'}, status=200)
        else:
            insert_query = f"INSERT INTO {table_name} (item_name,category_id,status,assigned_status,type,qty) VALUES (?,?,?,?,?,?)"
            insert_values = (item_name,category_id,"AVAILABLE","N",weapon_type,qty)
            cursor.execute(insert_query, insert_values)
            conn.commit()
            query=f"select id from {table_name} where category_id=? AND item_name=?"
            values=(category_id,item_name)
            cursor.execute(query,values)
            itemid=cursor.fetchone()
            itemid=itemid[0]
            query=f"UPDATE item set qr_id=? where id=?"
            values=(itemid,itemid)
            cursor.execute(query,values)
            conn.commit()
            query=f"select qr_id from item where item_name=?"
            values=(item_name,)
            cursor.execute(query,values)
            qr_id=cursor.fetchone()
            qr_id=qr_id[0]
            select_query = f"SELECT count(*) FROM inventory_data WHERE qr_id = ? AND category_id = ?"
            select_values = (qr_id,category_id)
            cursor.execute(select_query, select_values)
            inv_data=cursor.fetchone()
            logging.debug("count is " + str(inv_data[0]))
            if inv_data[0]==0:
                insert_query = f"INSERT INTO inventory_data (qr_id,category_id,qty,type) VALUES (?,?,?,?)"
                insert_values = (qr_id,category_id,qty,weapon_type)
                cursor.execute(insert_query, insert_values)
                conn.commit()
            cursor.close()
            conn.close()
            qr_code_data = {'Item name': item_name, 'QR ID': qr_id}
            qr_code_size = 250  # Adjust the size as per your requirement

            qr_image = generate_qr_code(qr_code_data, qr_code_size)
            file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
            qr_code_filename = file_path+ f"{qr_id}.png"
            logging.debug(qr_image.width,qr_image.height)
            qr_image.save(qr_code_filename)

            return JsonResponse({'sucess':qr_code_filename},safe=False)
def addtocategory_request(request):
    cursor,conn=connect_to_db()
    data = json.loads(request.body)
    table_name='category'
    cat=data.get('category')
    select_query = f"SELECT * FROM category WHERE category_name = ?"
    select_values = (cat,)
    cursor.execute(select_query, select_values)
    test_data = cursor.fetchall()
    if len(test_data)>0:
        cursor.close()
        conn.close()
        return JsonResponse({'success': 'Category Already present'}, status=400)
    else:

        insert_query = f"INSERT INTO {table_name} (category_name) VALUES (?)"
        insert_values = (cat,)
        cursor.execute(insert_query, insert_values)
        conn.commit()
        query="""select category_id,category_name from category where category_name=?"""
        values=(cat,)
        cursor.execute(query, values)
        data=cursor.fetchone()
        cursor.close()
        conn.close()
        return JsonResponse({'success': 'Category has been successfully added','id':data[0],'name':data[1]}, status=200)
def addtocategory(request):
    cursor,conn=connect_to_db()
    data = json.loads(request.body)
    table_name='category'
    cat=data.get('category')
    select_query = f"SELECT * FROM category WHERE category_name = ?"
    select_values = (cat,)
    cursor.execute(select_query, select_values)
    test_data = cursor.fetchall()
    if len(test_data)>0:
        cursor.close()
        conn.close()
        return JsonResponse({'success': 'Category Already present'}, status=400)
    else:

        insert_query = f"INSERT INTO {table_name} (category_name) VALUES (?)"
        insert_values = (cat,)
        cursor.execute(insert_query, insert_values)
        conn.commit()
        cursor.close()
        conn.close()
        return JsonResponse({'success': 'Category has been successfully added'}, status=200)

def fetch_category():
    cursor,conn=connect_to_db()
    select_query = f"SELECT category_id,category_name FROM category"
    cursor.execute(select_query)
    category_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return category_data
def change_status(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        cursor,conn=connect_to_db()
        status=data.get('status')
        empid=data.get('empid')
        query="""UPDATE user_man SET status=?  where userid=?"""
        values=(status,empid,)
        cursor.execute(query,values)
        conn.commit()
        return JsonResponse({'success':'Status Change Success'})
def edit_user(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        cursor,conn=connect_to_db()
        username=data.get('username')
        location=data.get('location')
        empid=data.get('empid')
        query="""UPDATE user_man SET name=?,location=? where userid=?"""
        values=(username,location,empid,)
        cursor.execute(query,values)
        conn.commit()
        return JsonResponse({'success':'User Edit Success'})
def reset_password(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        cursor,conn=connect_to_db()
        password=data.get('password')
        empid=data.get('empid')
        print(empid,password)
        password_enc=encode_password(password)
        print(password_enc)
        query="""UPDATE user_man SET password=? where userid=?"""
        values=(password_enc,empid,)
        cursor.execute(query,values)
        conn.commit()
        return JsonResponse({'success':'Password Reset Success'})


def search_user(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        cursor,conn=connect_to_db()
        searchInput=data.get('searchInput')
        user_type=data.get('user_type')
        status_type=data.get('status_type')
        if status_type=="active":
            status_type="A"
        elif status_type=="inactive":
            status_type="I"
        else:
            status_type=""
        if user_type=="id":
            query="""select empid,name,status,dated,location from user_man where empid LIKE ? and status LIKE ?"""
            values=("%{}%".format(searchInput),"%{}%".format(status_type))
            cursor.execute(query,values)
            user_data=cursor.fetchall()
            if user_data:
                items_data=[{'empid': item[0], 'name': item[1],'status':"ACTIVE" if item[2]=="A" else "INACTIVE",'dated':item[3],'location':item[4]} for item in user_data]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
        else:
            query="""select empid,name,status,dated,location from user_man where name LIKE ? and status LIKE ?"""
            values=("%{}%".format(searchInput),"%{}%".format(status_type))
            cursor.execute(query,values)
            user_data=cursor.fetchall()
            if user_data:
                items_data=[{'empid': item[0], 'name': item[1],'status':"ACTIVE" if item[2]=="A" else "INACTIVE",'dated':item[3],'location':item[4]} for item in user_data]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)

def create_user(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        cursor,conn=connect_to_db()
        name=data.get('name')
        id=data.get('id')
        location=data.get('location')
        password=data.get('password')
        status=data.get('status')
        password_enc=encode_password(password)
        select_query="""SELECT count(*) from user_man where empid =?"""
        select_values=(id,)
        cursor.execute(select_query,select_values)
        count=cursor.fetchone()
        if count[0]>0:
            return JsonResponse({'error':'User already Exists'},safe=False)
        else:
            query="""INSERT INTO user_man (userid,empid,password,name,location,status) VALUES(?,?,?,?,?,?)"""
            values=(id,id,password_enc,name,location,status)
            cursor.execute(query,values)
            conn.commit()
            return JsonResponse({'success': 'User Created Successfully'},safe=False)
@login_required
def register(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    context = {'username': username, 'location': location,'empid':empid}
    return render(request, 'register.html',context)
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_width, page_height = letter
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_width - 100, 20)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, x, y):
        page_num = len(self.pages)
        text = "Page %s" % page_num
        self.setFont("Helvetica", 12)
        self.drawString(x, y, text)

def create_report(data,title):
    file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\inventory_report.pdf"
    # Create a new PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter, showBoundary=0)

    # Add a custom PageTemplate to position the footer
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 40, id='normal')
    doc.addPageTemplates([PageTemplate(id='OneColumn', frames=frame)])
    # Create a PDF document using ReportLab
    
    elements = []

    # Add a title to the report
    title = title
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = 1
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20)) 
    # Add a table to display the inventory data
    table_data = []
    logging.debug(data[0])
    for item in data:
        table_data.append(item)

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    footer_text = "Generated on: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_style = styles["Normal"]
    footer_style.alignment = 2  # Right-align the footer
    elements.append(Spacer(1, 20))  # Add some space before the footer
    elements.append(Paragraph(footer_text, footer_style))
    # Build the PDF document
    doc.build(elements, canvasmaker=NumberedCanvas)
    
def download_pdf(request):
    logging.debug(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        table_data=data.get('data')
        type=data.get('type')
        print(table_data)
        if type=="Employee":
            create_report(table_data,"Employee Management Report")
        elif type=="Issues & Returns":
            create_report(table_data,"Issues and Returns Report")
        elif type=="Inventory":
            create_report(table_data,"Inventory Management Report")
        else:
            pass
        file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\inventory_report.pdf"
        with open(file_path, 'rb') as f:
            pdf_data = f.read()

        # Set the appropriate response headers for PDF download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'

        # Write the PDF data to the response
        response.write(pdf_data)
        return response
    return JsonResponse({'error': 'Invalid request method'},safe=False)
@login_required
def dashboard(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    conn = pypyodbc.connect(
            'Driver={SQL Server};'
            'Server=AUSU\\PROJECT;'
            'Database=zktimedb;'
            'uid=sa;'
            'pwd=uppolice'
        )

    cursor = conn.cursor()
    cursor.execute("""SELECT count(*) from USERINFO """)
    users = cursor.fetchone()
    logging.debug(users)
    users_count = users[0]
    cursor.execute("""SELECT count(*) from DEPARTMENTS """)
    dept = cursor.fetchone()
    dept_count = dept[0]
    cursor.execute("""SELECT count(*) from DEPARTMENTS """)
    dept = cursor.fetchone()
    dept_count = dept[0]
    context = {
        
        'users_count': users_count,
        'dept_count': dept_count,
        'returns_count': users_count,
        'employees_issued':users_count,
        'due_dates_passed':1,
        'username': username,
        'location': location,
        'empid':empid

    }
    return render(request, 'dashboard.html', context)


def download_excel(request):
    if request.method == 'POST':
        data = json.loads(request.body)['data']
        logging.debug(data)
        headers = data[0]
        rows = data[1:]
        # Create a pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)
        logging.debug(df)
        file_path=str(BASE_DIR)+"\\mysite\\static\\reports\\excel\\data.xlsx"
        output_file = file_path  # Specify the desired output file name and path
        workbook = Workbook(output_file)
        worksheet = workbook.add_worksheet()
        
        header_format = workbook.add_format({'bold': True})
        for j, header in enumerate(df.columns, start=1):
            worksheet.write(0, j-1, header, header_format)
        
        # Write the DataFrame values starting from the second row
        for i, row in enumerate(df.itertuples(index=False), start=1):
            
            for j, value in enumerate(row, start=1):
                worksheet.write(i, j-1, value)
        
        workbook.close()

        # Open the generated file
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=data.xlsx'
            return response

        return JsonResponse({'error': 'Invalid request method'},safe=False)
    return JsonResponse({'error': 'Invalid request method'},safe=False)
def generate_qr_code(data, size):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size // 25,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    return qr_image
def search_issues_returns(request):
    cursor,conn=connect_to_db()
    data=json.loads(request.body)
    from_date=data.get('from_date')
    to_date=data.get('to_date')
    to_date += ' 23:59:59'
    category_filter=data.get('category_filter')
    include_issues=data.get('include_issues')
    include_returns=data.get('include_returns')

    if include_issues==1 and include_returns==1:
        logging.debug(1)
        if category_filter==0:
            logging.debug(2)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ri.qty,CONVERT(varchar, ri.dated , 120)  AS receive_date FROM receive_inv ri JOIN emp_master em ON ri.emp_id = em.emp_id JOIN category c ON ri.category_id = c.category_id JOIN item it ON ri.qr_id = it.qr_id AND ri.category_id = it.category_id where (ri.dated BETWEEN ? AND ?) order by ri.dated desc "
            values=(from_date,to_date)
            cursor.execute(query,values)
            rec_items=cursor.fetchall()
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ii.qty,CONVERT(varchar, ii.dated , 120)  AS issue_date FROM issue_inv ii JOIN emp_master em ON ii.emp_id = em.emp_id JOIN category c ON ii.category_id = c.category_id JOIN item it ON ii.qr_id = it.qr_id AND ii.category_id = it.category_id where (ii.dated BETWEEN ? AND ?) order by ii.dated desc"
            values=(from_date,to_date)
            cursor.execute(query,values)
            iss_items=cursor.fetchall()
            if iss_items and rec_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                items_data=items_data + [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif rec_items:
                items_data=[{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif iss_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
        else:
            logging.debug(3)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ri.qty,CONVERT(varchar, ri.dated , 120) AS receive_date FROM receive_inv ri JOIN emp_master em ON ri.emp_id = em.emp_id JOIN category c ON ri.category_id = c.category_id JOIN item it ON ri.qr_id = it.qr_id AND ri.category_id = it.category_id where (ri.category_id=?) AND (ri.dated BETWEEN ? AND ?) order by ri.dated desc "
            values=(category_filter,from_date,to_date)
            cursor.execute(query,values)
            rec_items=cursor.fetchall()
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ii.qty,CONVERT(varchar, ii.dated , 120)  AS issue_date FROM issue_inv ii JOIN emp_master em ON ii.emp_id = em.emp_id JOIN category c ON ii.category_id = c.category_id JOIN item it ON ii.qr_id = it.qr_id AND ii.category_id = it.category_id where (ii.category_id=?) AND (ii.dated BETWEEN ? AND ?) order by ii.dated desc"
            values=(category_filter,from_date,to_date)
            cursor.execute(query,values)
            iss_items=cursor.fetchall()
            if iss_items and rec_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                items_data=items_data + [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif rec_items:
                items_data=[{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif iss_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
    elif include_issues==1:
        if category_filter==0:
            logging.debug(4)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ii.qty,CONVERT(varchar, ii.dated , 120)  AS issue_date FROM issue_inv ii JOIN emp_master em ON ii.emp_id = em.emp_id JOIN category c ON ii.category_id = c.category_id JOIN item it ON ii.qr_id = it.qr_id AND ii.category_id = it.category_id where (ii.dated BETWEEN ? AND ?) order by ii.dated desc"
            values=(from_date,to_date)
            cursor.execute(query,values)
            items=cursor.fetchall()

            if items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':"ISSUE",'date':item[5]} for item in items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
        else:
            logging.debug(5)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ii.qty,CONVERT(varchar, ii.dated , 120)  AS issue_date FROM issue_inv ii JOIN emp_master em ON ii.emp_id = em.emp_id JOIN category c ON ii.category_id = c.category_id JOIN item it ON ii.qr_id = it.qr_id AND ii.category_id = it.category_id where (ii.category_id=?) AND (ii.dated BETWEEN ? AND ?) order by ii.dated desc"
            values=(category_filter,from_date,to_date)
            cursor.execute(query,values)
            items=cursor.fetchall()

            if items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':"ISSUE",'date':item[5]} for item in items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
    elif include_returns==1:
        if category_filter==0:
            logging.debug(6)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ri.qty,CONVERT(varchar, ri.dated , 120)  AS receive_date FROM receive_inv ri JOIN emp_master em ON ri.emp_id = em.emp_id JOIN category c ON ri.category_id = c.category_id JOIN item it ON ri.qr_id = it.qr_id AND ri.category_id = it.category_id where (ri.dated BETWEEN ? AND ?) order by ri.dated desc"
            values=(from_date,to_date)
            cursor.execute(query,values)
            items=cursor.fetchall()

            if items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
        else:
            logging.debug(7)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ri.qty,CONVERT(varchar, ri.dated , 120)  AS receive_date FROM receive_inv ri JOIN emp_master em ON ri.emp_id = em.emp_id JOIN category c ON ri.category_id = c.category_id JOIN item it ON ri.qr_id = it.qr_id AND ri.category_id = it.category_id where (ri.category_id=?) AND (ri.dated BETWEEN ? AND ?) order by ri.dated desc "
            values=(category_filter,from_date,to_date)
            cursor.execute(query,values)
            items=cursor.fetchall()

            if items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
    else:
        if category_filter==0:
            logging.debug(8)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ri.qty,CONVERT(varchar, ri.dated , 120)  AS receive_date FROM receive_inv ri JOIN emp_master em ON ri.emp_id = em.emp_id JOIN category c ON ri.category_id = c.category_id JOIN item it ON ri.qr_id = it.qr_id AND ri.category_id = it.category_id where (ri.dated BETWEEN ? AND ?) order by ri.dated desc "
            values=(from_date,to_date)
            cursor.execute(query,values)
            rec_items=cursor.fetchall()
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ii.qty,CONVERT(varchar, ii.dated , 120)  AS issue_date FROM issue_inv ii JOIN emp_master em ON ii.emp_id = em.emp_id JOIN category c ON ii.category_id = c.category_id JOIN item it ON ii.qr_id = it.qr_id AND ii.category_id = it.category_id where (ii.dated BETWEEN ? AND ?) order by ii.dated desc"
            values=(from_date,to_date)
            cursor.execute(query,values)
            iss_items=cursor.fetchall()
            if iss_items and rec_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                items_data=items_data + [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif rec_items:
                items_data=[{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif iss_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)
        else:
            logging.debug(9)
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ri.qty,CONVERT(varchar, ri.dated , 120)  AS receive_date FROM receive_inv ri JOIN emp_master em ON ri.emp_id = em.emp_id JOIN category c ON ri.category_id = c.category_id JOIN item it ON ri.qr_id = it.qr_id AND ri.category_id = it.category_id where (ri.category_id=?) AND (ri.dated BETWEEN ? AND ?)  order by ri.dated desc"
            values=(category_filter,from_date,to_date)
            cursor.execute(query,values)
            rec_items=cursor.fetchall()
            query = f"SELECT em.emp_id,em.emp_name,c.category_name,it.item_name,ii.qty,CONVERT(varchar, ii.dated , 120)  AS issue_date FROM issue_inv ii JOIN emp_master em ON ii.emp_id = em.emp_id JOIN category c ON ii.category_id = c.category_id JOIN item it ON ii.qr_id = it.qr_id AND ii.category_id = it.category_id where (ii.category_id=?) AND (ii.dated BETWEEN ? AND ?) order by ii.dated desc"
            values=(category_filter,from_date,to_date)
            cursor.execute(query,values)
            iss_items=cursor.fetchall()
            if iss_items and rec_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                items_data=items_data + [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif rec_items:
                items_data=[{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'RETURN','date':item[5]} for item in rec_items]
                return JsonResponse(items_data, safe=False)
            elif iss_items:
                items_data = [{'emp_id': item[0], 'emp_name': item[1],'category':item[2],'item_name':item[3],'qty':item[4],'type':'ISSUE','date':item[5]} for item in iss_items]
                return JsonResponse(items_data, safe=False)
            else:
                return JsonResponse([{'error':'No records available'}], safe=False)

@login_required
def issue_receive(request):

    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    if request.method == 'GET':
        today = datetime.date.today()
        cat=fetch_category()
        category_dict = dict(cat)
        context = {'username': username, 'location': location,'empid':empid,'today': today,'categories':category_dict}
        return render(request, 'issue_receive.html', context)
    context = {'username': username, 'location': location,'empid':empid}
    return render(request, 'issue_receive.html', context)

def check_qr(request):
    data=json.loads(request.body)
    cursor,conn=connect_to_db()
    qr_id=data.get('qr_id')
    query=f"select count(*) from item where qr_id=?"
    values=(qr_id,)
    cursor.execute(query,values)
    qr=cursor.fetchone()
    if qr[0]==0:
        return JsonResponse({'success':'QR ID Does not Exist'}, status=200)
    else:
        return JsonResponse({'success':'QR ID Exists'}, status=200)
def generate_pdf_with_qr_id(request):
    data=json.loads(request.body)
    cursor,conn=connect_to_db()
    position=data.get('position')
    qr_id=data.get('qr_id')
    query=f"select item_name from item where qr_id=?"
    values=(qr_id,)
    cursor.execute(query,values)
    item_name=cursor.fetchone()
    item_name=item_name[0]
    file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
    logging.debug(file_path)
    qr_code_filename = file_path+ f"{qr_id}.png"
    logging.debug(position,item_name,qr_code_filename,qr_id)
    doc = FPDF()

    block_width = 50  # Block width in mm
    block_height = 36 # Block height in mm
    block_margin = 2  # Block margin in mm
    doc.add_page()
    # for i in range(1,19):
        # Calculate the x and y coordinates based on the selected position
    selected_block = int(position)
    blocks_per_row = 3  # Number of blocks per row
    x = ((selected_block - 1) % blocks_per_row) * (block_width + block_margin)
    y = 5 + ((selected_block - 1) // blocks_per_row) * (block_height + block_margin)

        # Add the QR code image to the PDF at the specified position
    doc.image(qr_code_filename, x, y, block_width, block_height)
    logging.debug(x,y)
        # Add the entered text above the QR code
    doc.set_font("Arial", 'B',size=8)
    doc.text(x+10, y+2 , str(qr_id))
    doc.text(x+35, y+2 , item_name)

    save_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\QR_Code.pdf"
    # Save the PDF with a unique filename
    doc.output(save_path)
    cursor.close()
    conn.close()
    return JsonResponse({'success':'Item with QR ID '+ str(qr_id) + ' has been generated'}, status=200)

def generate_pdf_with_qr_codes(request):
    data=json.loads(request.body)
    cursor,conn=connect_to_db()
    position=data.get('position')
    item_name=data.get('item_name')
    query=f"select qr_id from item where item_name=?"
    values=(item_name,)
    cursor.execute(query,values)
    qr_id=cursor.fetchone()
    qr_id=qr_id[0]
    file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
    qr_code_filename = file_path+ f"{qr_id}.png"
    logging.debug(position,item_name,qr_code_filename,qr_id)
    doc = FPDF()

    block_width = 70  # Block width in mm
    block_height = 46 # Block height in mm
    block_margin = 2  # Block margin in mm
    doc.add_page()
    # for i in range(1,19):
        # Calculate the x and y coordinates based on the selected position
    selected_block = int(position)
    blocks_per_row = 3  # Number of blocks per row
    x = ((selected_block - 1) % blocks_per_row) * (block_width + block_margin)
    y = 5 + ((selected_block - 1) // blocks_per_row) * (block_height + block_margin)

        # Add the QR code image to the PDF at the specified position
    doc.image(qr_code_filename, x, y, block_width, block_height)
    logging.debug(x,y)
        # Add the entered text above the QR code
    doc.set_font("Arial", 'B',size=8)
    doc.text(x+10, y+2 , str(qr_id))
    doc.text(x+35, y+2 , item_name)

    save_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\QR_Code.pdf"
    # Save the PDF with a unique filename
    doc.output(save_path)
    cursor.close()
    conn.close()
    return JsonResponse({'success':'Item with QR ID '+ str(qr_id) + ' has been added to Inventory'}, status=200)
def generate_qr_code_view(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        category_name=data.get('category_name')
        item_name=data.get('item_name')
        weapon_type=data.get('type')
        qty=data.get('qty')
        table_name='item'
        cursor,conn=connect_to_db()
        select_query=f"SELECT category_id from category where category_name=?"
        select_values=(category_name,)
        cursor.execute(select_query,select_values)
        category_id=cursor.fetchone()
        category_id=category_id[0]
        select_query = f"SELECT * FROM item WHERE  item_name=?"
        select_values = (item_name,)
        cursor.execute(select_query, select_values)
        item_data = cursor.fetchall()
        if len(item_data)>0:
            cursor.close()
            conn.close()
            return JsonResponse({'success': 'Item already exists'}, status=200)
        else:
            insert_query = f"INSERT INTO {table_name} (item_name,category_id,status,assigned_status,type,qty) VALUES (?,?,?,?,?,?)"
            insert_values = (item_name,category_id,"AVAILABLE","N",weapon_type,qty)
            cursor.execute(insert_query, insert_values)
            conn.commit()
            query=f"select id from {table_name} where category_id=? AND item_name=?"
            values=(category_id,item_name)
            cursor.execute(query,values)
            itemid=cursor.fetchone()
            itemid=itemid[0]
            query=f"UPDATE item set qr_id=? where id=?"
            values=(itemid,itemid)
            cursor.execute(query,values)
            conn.commit()
            query=f"select qr_id from item where item_name=?"
            values=(item_name,)
            cursor.execute(query,values)
            qr_id=cursor.fetchone()
            qr_id=qr_id[0]
            select_query = f"SELECT count(*) FROM inventory_data WHERE qr_id = ? AND category_id = ?"
            select_values = (qr_id,category_id)
            cursor.execute(select_query, select_values)
            inv_data=cursor.fetchone()
            logging.debug("count is " + str(inv_data[0]))
            if inv_data[0]==0:
                insert_query = f"INSERT INTO inventory_data (qr_id,category_id,qty,type) VALUES (?,?,?,?)"
                insert_values = (qr_id,category_id,qty,weapon_type)
                cursor.execute(insert_query, insert_values)
                conn.commit()
            cursor.close()
            conn.close()
            qr_code_data = {'Item name': item_name, 'QR ID': qr_id}
            qr_code_size = 250  # Adjust the size as per your requirement

            qr_image = generate_qr_code(qr_code_data, qr_code_size)
            file_path=str(BASE_DIR)+"\\mysite\\static\\pdfs\\"
            qr_code_filename = file_path+ f"{qr_id}.png"
            logging.debug(qr_image.width,qr_image.height)
            qr_image.save(qr_code_filename)

            return JsonResponse({'sucess':qr_code_filename},safe=False)
@login_required
def stock_master(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    cat=fetch_category()
    category_dict = dict(cat)
    context = {'categories':category_dict,'username': username, 'location': location,'empid':empid}
    return render(request,'stock_master.html',context)
@login_required
def request_stock(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    cat=fetch_category()
    category_dict = dict(cat)
    context = {'categories':category_dict,'username': username, 'location': location,'empid':empid}
    return render(request,'request_stock.html',context)
@login_required
def issue_stock(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    cat=fetch_category()
    category_dict = dict(cat)
    context = {'categories':category_dict,'username': username, 'location': location,'empid':empid}
    return render(request,'issue_stock.html',context)
@login_required
def receive_stock(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    cat=fetch_category()
    category_dict = dict(cat)
    context = {'categories':category_dict,'username': username, 'location': location,'empid':empid}
    return render(request,'receive_stock.html',context)
@login_required
def qr_code(request):
    username = request.session.get('username')
    location = request.session.get('location')
    empid = request.session.get('empid')
    cat=fetch_category()
    category_dict = dict(cat)
    context = {'categories':category_dict,'username': username, 'location': location,'empid':empid}
    return render(request,'qr_code.html',context)
def logout_view(request):
    logout(request)
    return redirect('/')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        logging.debug(request.user.is_authenticated)
        cursor,conn=connect_to_db()
        if user is not None:
            login(request, user)
            logging.debug("checking if user is authenticated")
            logging.debug(request.user.is_authenticated)
            select_query = f"SELECT * FROM user_man WHERE userid = ?"
            select_values = (username,)
            cursor.execute(select_query, select_values)
            user_data = cursor.fetchone()
            request.session['username'] = user_data[3]
            request.session['location'] = user_data[5]
            request.session['empid'] = user_data[4]
            
            if user_data[6]=='I':
                error = "User Inactive"
                return render(request, 'login.html', {'error': error})
            else:
                return redirect('/register')  # redirect to a success page
        else:
            error = "Invalid username or password."
            return render(request, 'login.html', {'error': error})



    return render(request, 'login.html')
