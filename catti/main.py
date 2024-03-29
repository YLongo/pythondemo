import os.path
import re
from datetime import datetime

import fitz
import jieba
import nltk
import pytesseract
from docx import Document
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import youdao_parser
from ECDICT import stardict

# pdf and docx directory
file_input_dir = r"${file_input_dir}"
# image output directory
image_output = r"${image_output}"
# text output directory
# text_output = r"${text_output}"
text_output = r"D:\CATTI\text"

# image ocr output directory
# image_2_text_output = r"${image_2_text_output}"
image_2_text_output = r"D:\CATTI\image2text"


def recoverpix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask

    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = fitz.Pixmap(doc, xref)
        pix = fitz.Pixmap(fitz.csRGB, pix)
        return {  # create dictionary expected by caller
            "ext": "png",
            "colorspace": 3,
            "image": pix.tobytes("png"),
        }

    # special case: /SMask or /Mask exists
    if smask > 0:
        pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
        mask = fitz.Pixmap(doc.extract_image(smask)["image"])
        pix = fitz.Pixmap(pix0, mask)
        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"

        return {  # create dictionary expected by caller
            "ext": ext,
            "colorspace": pix.colorspace.n,
            "image": pix.tobytes(ext),
        }

    return doc.extract_image(xref)


def extract_text_and_img(dir_path):
    """
    get text and image from pdf and get text from docx
    """
    # if dir_path is not dir
    if not os.path.isdir(dir_path):
        return

    # get all full file name in dir_path
    file_name_list = os.listdir(dir_path)
    for full_file_name in file_name_list:
        file_path = os.path.join(dir_path, full_file_name)
        print("file_path:", file_path)

        if full_file_name.endswith(".pdf"):
            extract_from_pdf(file_path)
        elif full_file_name.endswith(".docx"):
            extract_from_docx(file_path)


def extract_from_pdf(full_file_path):
    file_path, file_name, suffix = split_file(full_file_path)

    if not suffix == ".pdf":
        return

    doc = fitz.open(full_file_path)
    for page in doc:
        text = page.get_text()
        save_text(text, os.path.join(text_output, file_name + ".txt"))
        images = page.get_images()
        print("images:", len(images))
        number = page.number
        print("number:", number)
        save_img_from_pdf(doc, images, file_name)


def extract_from_docx(full_file_path):
    """
    extract text from docx
    (only support docx)
    """

    (file_path, file_name, suffix) = split_file(full_file_path)

    if not file_name.endswith(".docx"):
        return

    text_output_path = os.path.join(text_output, file_name + ".txt")
    # print("file_name:", file_name)

    # create an instance of a
    # word document we want to open
    doc = Document(file_path)

    # for printing the complete document
    for para in doc.paragraphs:
        save_text(para.text, text_output_path)


def save_text(text, text_output_path):
    if len(text) == 0:
        return
    with open(text_output_path, "ab") as out:  # open text output
        out.write(text.encode("utf-8"))


def save_img_from_pdf(doc, images, file_name):
    if len(images) == 0:
        return
    for img in images:
        xref = img[0]
        width = img[2]
        height = img[3]
        print(f"width: {width}, height: {height}")
        image = recoverpix(doc, img)
        imgdata = image["image"]
        # print("file_name:", file_name)
        imgfile = os.path.join(image_output, "%s-%05i.%s" % (file_name, xref, image["ext"]))
        if os.path.exists(imgfile):
            return
        with open(imgfile, "wb") as fout:
            fout.write(imgdata)


def split_file(file_path_name):
    """
    get file path and file name and suffix
    """
    (file_path, full_file_name) = os.path.split(file_path_name)
    (name, suffix) = os.path.splitext(full_file_name)
    # print(file_path)
    # print(full_file_name)
    return file_path, name, suffix


def ocr_text(file_path):
    """
    ocr text from image
    """
    start = datetime.now()
    # languages = pytesseract.get_languages()
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    full_name_list = os.listdir(image_output)
    for full_name in full_name_list:
        full_file_path = os.path.join(image_output, full_name)
        result = pytesseract.image_to_string(full_file_path, lang='chi_sim+eng')
        with open(os.path.join(image_2_text_output, "image-orc.txt"), "ab") as out:
            out.write(result.encode("utf-8"))

        # print(result)
    end = datetime.now()
    print(end - start)


def stopwordslist(filepath):
    return [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()
            if not line.strip().startswith('#')]


def cut_words(text):
    stopwords = stopwordslist('stopwords.txt')
    words = jieba.cut(text)
    result_words = []
    for r in words:
        r = r.strip()
        if r == '':
            continue

        r = r.lower()

        # remove stopwords and digits
        if r in stopwords or r.isdigit():
            continue

        if not r.isalpha():
            continue
        # remove chinese characters
        if re.search(u'[\u4e00-\u9fff]', r):
            continue

        result_words.append(r)
        result_words.append('\n')
    return result_words


def nlp_output():
    # nlp_output = r'${nlp_output}'
    nlp_output = r'D:\CATTI\nlp'
    nlp_output_file = os.path.join(nlp_output, 'output.txt')

    full_file_path_list = []
    image_2_text_full_file_name_list = os.listdir(image_2_text_output)
    for text_full_file_name in image_2_text_full_file_name_list:
        text_full_file_path = os.path.join(image_2_text_output, text_full_file_name)
        full_file_path_list.append(text_full_file_path)

    text_full_file_name_list = os.listdir(text_output)
    for text_full_file_name in text_full_file_name_list:
        text_full_file_path = os.path.join(text_output, text_full_file_name)
        full_file_path_list.append(text_full_file_path)

    for file_path in full_file_path_list:
        # print(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            result = f.read()
            words = cut_words(result)
            with open(nlp_output_file, 'a', encoding='utf-8') as f:
                f.writelines(words)


def word_convert_xml(word_list, xml_dir):
    """
    convert word list to youdao import xml format
    """

    xml_name = "youdao.xml"
    tag = "CATTI"

    count = 0
    split_count = 0

    # temp_xml_name = str(split_count) + "_" + xml_name
    # xml_file = open(os.path.join(xml_dir, temp_xml_name), 'w', encoding='utf-8')
    xml_file = None

    for word in word_list:

        # split xml for youdao limit
        if count % 10000 == 0:
            split_count += 1
            temp_xml_name = str(split_count) + "_" + xml_name
            xml_file = open(os.path.join(xml_dir, temp_xml_name), 'w', encoding='utf-8')
            xml_file.write('<wordbook>')  # xml head

        xml_file.write('<item>')
        xml_file.write('    <word>' + word + '</word>\n')
        # xml_file.write('    <trans>' + '<![CDATA[]]>' + '</trans>\n')
        xml_file.write('    <tags>' + f"{tag}" + '</tags>\n')  # 有道词典中的单词分组名
        xml_file.write('    <progress>0</progress>\n')
        xml_file.write('</item>')

        count += 1
        if count % 10000 == 0:
            xml_file.write('</wordbook>')  # xml tail

    # if len(word_list) % 1000 != 0:
    xml_file.write('</wordbook>')

    xml_file.close()


def save_to_youdao_dict():
    """
    save word list to youdao dict
    """
    input_path = r'./CATTI/youdao_output.txt'
    word_count = {}

    with open(input_path, 'r', encoding='utf-8') as words:
        for word in words:
            # print(word.strip())
            word = word.strip()
            if not word.isalpha():
                continue
            word_count[word] = word_count.get(word, 0) + 1

    sorted(word_count, key=word_count.get, reverse=True)

    output_path = r'./CATTI'
    word_convert_xml(word_count, output_path)


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        # print("tag:" + tag)
        return None


def nltk_lemm():
    # nltk.download('wordnet')
    # nltk.download('omw-1.4')
    # nltk.download('punkt')
    # nltk.download('stopwords')
    # nltk.download('averaged_perceptron_tagger')

    input_put_text = r'D:\CATTI\nlp\catti.txt'
    clean_output_text = r'D:\CATTI\nlp\clean_output.txt'

    # stemmer = SnowballStemmer("english", ignore_stopwords=True)

    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    stop_words += stopwordslist('stopwords.txt')
    print(stop_words)

    # tags = nltk.pos_tag(["ofturkeys"])
    # tag = tags[0]
    # print(tags)
    # print(lemmatizer.lemmatize(tag[0], get_wordnet_pos(tag[1])))
    #
    # tags = nltk.pos_tag(["abandoned"])
    # tag = tags[0]
    # print(tags)
    # print(lemmatizer.lemmatize(tag[0], get_wordnet_pos(tag[1])))

    print("--- --- ---")

    clean_words = set()

    with open(input_put_text, 'r', encoding='utf-8') as f:
        words = f.readlines()

        for w in words:
            w = w.strip()
            if len(w) <= 1:
                continue

            if not w.isalpha():
                continue

            if w in stop_words:
                continue

            clean_words.add(w)

    lemm_word_set = set()

    for word in clean_words:

        tags = nltk.pos_tag([word])
        tag = tags[0]

        pos = get_wordnet_pos(tag[1])
        if pos is None:
            lemmatize = lemmatizer.lemmatize(tag[0])
            lemm_word_set.add(lemmatize + '\n')
            continue

        lemmatize = lemmatizer.lemmatize(tag[0], pos)
        lemm_word_set.add(lemmatize + '\n')

    clean_words_list = sorted(lemm_word_set)

    with open(clean_output_text, 'w', encoding='utf-8') as f:
        f.writelines(clean_words_list)


def query_youdao():
    input_text = r'./output.txt'
    api = youdao_parser.API
    youdao_output_text = r'./CATTI/youdao_output.txt'
    youdao_words = set()
    count = 0
    with open(input_text, mode='r') as f:
        lines = f.readlines()

        for line in lines:
            queryResult = api.query(line.strip())
            definition_ = queryResult['definition']
            if definition_:
                youdao_words.add(line)

            count += 1
            if count % 1000 == 0:
                print(count)
    with open(youdao_output_text, mode='w') as f:
        f.writelines(youdao_words)

def clean_with_ecdict():
    input_text = r'./output.txt'
    youdao_output_text = r'./CATTI/youdao_output.txt'
    youdao_words = set()
    count = 0

    # clear data
    with open(youdao_output_text, mode='w') as f:
        pass

    db = os.path.join(os.path.dirname(__file__), 'star_dict.db')
    sd = stardict.StarDict(db, False)

    with open(input_text, mode='r') as f:
        lines = f.readlines()

        for line in lines:
            # csv_name = os.path.join(os.path.dirname(__file__), '../ECDICT/stardict.csv')
            # dc = stardict.StarDict(csv_name)

            line = line.strip()
            query_result = sd.query(line)
            if query_result:
                youdao_words.add(line + '\n')

            count += 1
            if count % 1000 == 0:
                print(count)

    with open(youdao_output_text, mode='a') as f:
        f.writelines(youdao_words)


if __name__ == "__main__":
    # extract_text_and_img(file_input_dir)
    # extract_from_docx(file_input_dir)
    # extract_from_pdf(file_input_01)
    # ocr_text(image_output)
    # nlp_output()
    save_to_youdao_dict()
    # nltk_lemm()
    # query_youdao()

    # youdao_output_text = r'D:\CATTI\nlp\youdao_output.txt'
    # with open(youdao_output_text, mode='r') as f:
    #     lines = f.readlines()
    #
    #     sorted_lines = sorted(lines)
    #     with open(youdao_output_text, mode='w') as f:
    #         f.writelines(sorted_lines)
    # extract_from_pdf(file_input_01)

    # just only exec once
    # stardict.convert_dict('star_dict.db', '../ECDICT/stardict.csv')
    # clean_with_ecdict()
