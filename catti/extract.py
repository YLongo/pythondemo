# import time
#
# import PyPDF2
# import pdfplumber
# from PIL import Image
#
#
# def extract_image(page):
#     try:
#         if '/XObject' in page['/Resources']:
#             xObject = page['/Resources']['/XObject'].getObject()
#             for obj in xObject:
#                 if xObject[obj]['/Subtype'] == '/Image':
#                     size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
#                     data = xObject[obj].getData()
#                     if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
#                         mode = "RGB"
#                     else:
#                         mode = "P"
#                     # 保存图片的文件名前缀
#                     img_pre = str(int(time.time()*1000))
#                     if '/Filter' in xObject[obj]:
#                         if xObject[obj]['/Filter'] == '/FlateDecode':
#                             img = Image.frombytes(mode, size, data)
#                             img.save(img_pre + ".png")
#                         elif xObject[obj]['/Filter'] == '/DCTDecode':
#                             img = open(img_pre + ".jpg", "wb")
#                             img.write(data)
#                             img.close()
#                         elif xObject[obj]['/Filter'] == '/JPXDecode':
#                             img = open(img_pre + ".jp2", "wb")
#                             img.write(data)
#                             img.close()
#                         elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
#                             img = open(img_pre + ".tiff", "wb")
#                             img.write(data)
#                             img.close()
#                     else:
#                         img = Image.frombytes(mode, size, data)
#                         img.save(img_pre + ".png")
#         else:
#             print("本页无图片")
#     except:
#         print("图片提取失败")
#
#
# def extract_content(pdf_path):
#     # 内容提取，使用 pdfplumber 打开 PDF，用于提取文本
#     with pdfplumber.open(pdf_path) as pdf_file:
#         # 使用 PyPDF2 打开 PDF 用于提取图片
#         pdf_image_reader = PyPDF2.PdfFileReader(open(pdf_path, "rb"))
#         print(pdf_image_reader.getNumPages())
#
#         content = ''
#         # len(pdf.pages)为PDF文档页数，一页页解析
#         for i in range(len(pdf_file.pages)):
#             print("当前第 %s 页" % i)
#             # pdf.pages[i] 是读取PDF文档第i+1页
#             page_text = pdf_file.pages[i]
#             # page.extract_text()函数即读取文本内容
#             page_content = page_text.extract_text()
#             if page_content:
#                 content = content + page_content + "\n"
#                 print(page_content)
#
#             # 提取图片
#             page_image = pdf_image_reader.getPage(pageNumber=i)
#             extract_image(page_image)
#
#
# if __name__ == '__main__':
#     pdf_file = "../media/AliDouble11.pdf"
#     extract_content(pdf_file)
