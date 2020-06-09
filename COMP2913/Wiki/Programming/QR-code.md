1.  import qrcode 
2.  qr = qrcode.QRCode(     
3.     version=1,     
4.     error_correction=qrcode.constants.ERROR_CORRECT_L,     
5.     box_size=10,     
6.     border=4, 
7.  ) 
8.  qr.add_data('hello, qrcode') 
9.  qr.make(fit=True)  
10. img = qr.make_image()
11. img.save('123.png')