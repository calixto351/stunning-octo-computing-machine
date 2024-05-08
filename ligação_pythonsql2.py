
from flask import Flask,render_template,request,flash,redirect,session,jsonify,url_for,send_file,send_file,current_app,make_response
from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, ALL_ATTRIBUTES, ALL
from flask_bcrypt import Bcrypt
import tempfile
import mysql.connector
import requests
import urllib
import shutil
from connfig import SECRET_KEY
import math
import schedule
import threading
import sys
from flask_sslify import SSLify
from functools import wraps
import getpass
import socket
import win32api
import platform
import base64
import subprocess
import re
import psutil
import hashlib
import jwt
import tabula
from bs4 import BeautifulSoup
import csv
import pandas as pd
import sqlalchemy.ext
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine, Column, Integer, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
import json
import os
from  dotenv import load_dotenv
from datetime import date,datetime,timedelta, time
from datetime import datetime, time
from time import sleep
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from openpyxl.drawing.image import Image as XLImage
from openpyxl import Workbook
import openpyxl
import PyPDF2
from pdf2image import convert_from_bytes, convert_from_path
from pdf2docx import Converter
from docx import Document
from PIL import Image as PILImage
from fpdf import FPDF
from PyPDF2 import PdfReader
from PyPDF2 import PdfMerger
from PyPDF2 import PdfWriter
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import NameObject, FloatObject, createStringObject
import img2pdf
from decimal import Decimal
import fitz
import io
from io import BytesIO
import xlsxwriter

def informacoes():
    Base = declarative_base()
    load_dotenv()
    con = mysql.connector.connect(host='',database='',user='',password="")
    mycursor = con.cursor(buffered=True)
    app = Flask(__name__,template_folder='',static_folder='')
    sslify = SSLify(app)
    scheduler = BackgroundScheduler()
    app.secret_key = os.urandom(24)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DOWNLOAD_FOLDER'] = os.path.join(os.getcwd(), 'downloads')
    output_directory = 'C:\\Desktop\\downloads'
    os.makedirs(output_directory, exist_ok=True)
    logged_users = set()
    con.commit()
    print(app.config['SECRET_KEY'])
#------------------------------------------------#
informacoes()
@app.route('/assinatura', methods=['POST'])
def assinatura():
    return render_template("(Assinar documentos).html")
def get_download_folder():
    if platform.system() == 'Darwin':
        return os.path.expanduser('~/Downloads')
    elif platform.system() == 'Windows':
        return os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        return os.path.expanduser('~/Downloads')
@app.route('/CompressPDF', methods=['POST'])
def comprimir_pdf():
    if 'pdf_file' not in request.files:
        return 'Nenhum arquivo PDF fornecido.'
    pdf_file = request.files['pdf_file']
    if pdf_file.filename.endswith('.pdf'):
        compress_quality = 50  # Ajuste a qualidade de compressão aqui (0-100)
        # Criar um arquivo temporário para salvar o PDF comprimido
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_pdf_path = temp_file.name
            # Salvar o arquivo PDF fornecido temporariamente
            pdf_file.save(temp_pdf_path)
            # Comprimir o PDF usando pdf2image e PIL
            images = convert_from_bytes(open(temp_pdf_path, 'rb').read())
            compressed_images = []
            for image in images:
                # Convertendo para o modo RGB para garantir compatibilidade com JPEG
                image_rgb = image.convert('RGB')
                # Criando uma nova imagem com qualidade de compressão
                new_image = Image.new("RGB", image_rgb.size)
                new_image.putdata(list(image_rgb.getdata()))
                # Salvando a imagem comprimida na lista
                compressed_images.append(new_image)
            # Salvando as imagens comprimidas em um arquivo PDF
            compressed_images[0].save(temp_pdf_path, "PDF", quality=compress_quality, save_all=True, append_images=compressed_images[1:])
            # Enviar o arquivo comprimido para download
            return send_file(temp_pdf_path, mimetype='application/pdf', as_attachment=True, download_name='compressed.pdf')
            # Excluir o arquivo temporário
            try:
                os.remove(temp_pdf_path)
            except OSError:
                pass
    return 'O arquivo fornecido não é um PDF válido.'
@app.route('/PDFToImages', methods=['POST'])
def converter_pdf_para_imagens():
    if 'pdf_file' not in request.files:
        return 'Nenhum arquivo PDF fornecido.'

    pdf_file = request.files['pdf_file']

    images = convert_from_bytes(pdf_file.read(), dpi=200)

    image_buffers = []  # Lista para armazenar os buffers de imagem

    for i, image in enumerate(images):
        image_buffer = io.BytesIO()  # Buffer para armazenar a imagem
        image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)  # Reinicia o ponteiro do buffer para o início
        image_buffers.append(image_buffer)

    # Faz o download de cada imagem individualmente
    temp_dir = tempfile.mkdtemp()

    # Salve as imagens temporárias no diretório
    for i, image in enumerate(images):
        image_path = os.path.join(temp_dir, f'image_{i}.jpg')
        image.save(image_path, 'JPEG')

    # Compacte as imagens em um arquivo ZIP
    zip_filename = os.path.join(temp_dir, 'images.zip')
    shutil.make_archive(zip_filename, 'zip', temp_dir)

    # Envie o arquivo ZIP como resposta
    return send_file(zip_filename, mimetype='application/zip', as_attachment=True)
def convert_word_to_pdf(word_file):
    try:
        # Abrir o arquivo do Word
        doc = Document(word_file)

        # Converter o arquivo do Word para PDF
        pdf_bytes = BytesIO()
        pdf_converter = Converter(doc, pdf_bytes)
        pdf_converter.convert()
        pdf_converter.close()

        return pdf_bytes.getvalue()

    except Exception as e:
        print(f"Erro ao converter arquivo: {str(e)}")
        return None
@app.route('/WordToPDF', methods=['POST'])
def word_to_pdf():
    if 'wordtopdf' not in request.files:
        return 'Nenhum arquivo do Word fornecido.'

    word_file = request.files['wordtopdf']

    if word_file.filename == '':
        return 'Nenhum arquivo selecionado.'

    if word_file and word_file.filename.endswith('.docx'):
        try:
            # Salvar o arquivo do Word em um local temporário
            temp_word_file = 'temp.docx'
            word_file.save(temp_word_file)

            # Converter o arquivo do Word para PDF
            output_path = 'converted.pdf'
            Converter(temp_word_file, output_path)

            # Ler o arquivo PDF convertido
            with open(output_path, 'rb') as f:
                pdf_data = f.read()

            # Configurar a resposta com o arquivo PDF
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=converted.pdf'

            return response

        except Exception as e:
            print(f"Erro ao converter arquivo{str(e)}:")
            return 'Erro ao converter o arquivo.'

    return 'O arquivo fornecido não é um documento do Word válido.'
@app.route('/World', methods=['POST'])
def converter_pdf_para_world():
    # Verifica se o arquivo PDF foi enviado
    if 'pdf_file' not in request.files:
        return "Nenhum arquivo PDF foi enviado."

    pdf_file = request.files['pdf_file']

    # Verifica se o arquivo PDF tem uma extensão válida
    if pdf_file.filename.endswith('.pdf'):
        # Caminho para o arquivo PDF temporário
        output_path = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'output.docx')
        pdf_path = 'temp.pdf'
        pdf_file.save(pdf_path)

        # Caminho para o arquivo Word temporário
        docx_path = 'temp.docx'

        # Converte o arquivo PDF em Word
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()

        # Remove o arquivo PDF temporário
        os.remove(pdf_path)

        # Envia o arquivo Word para download
        return send_file(docx_path, as_attachment=True)

    return "O arquivo enviado não é um PDF válido."
@app.route('/Excell',methods=['POST'])
def converter_foto_para_excell_consertarisso():
    if 'imagens' not in request.files:
        return 'Nenhuma imagem fornecida.'

    imagens = request.files.getlist('imagens')

    if not imagens:
        return 'Nenhum arquivo selecionado.'

    # Cria um novo Workbook
    workbook = Workbook()

    # Cria uma nova planilha
    sheet = workbook.active
    sheet.title = 'Planilha 1'

    # Itera sobre as imagens
    for i, imagem in enumerate(imagens, start=1):
        if imagem.filename == '':
            continue

        # Lê o conteúdo da imagem
        image_data = imagem.read()

        # Cria um objeto Image
        img = XLImage(io.BytesIO(image_data))

        # Insere a imagem na primeira célula da planilha
        sheet.add_image(img, f'A{i}')

    # Define o nome do arquivo de saída
    output_excel = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'imagens.xlsx')

    # Salva o arquivo Excel
    workbook.save(output_excel)

    # Envia o arquivo Excel para download
    return send_file(output_excel, as_attachment=True)
@app.route('/Foto', methods=['POST'])
def converter_imagem_para_pdf(pdf_buffer=None):
    if pdf_buffer is None:
        pdf_buffer = BytesIO()
    # Verifica se o formulário contém arquivos de imagem
    if 'imagens' not in request.files:
        return 'Nenhuma imagem fornecida.'

    imagens = request.files.getlist('imagens')

    if not imagens:
        return 'Nenhum arquivo selecionado.'

    # Cria um objeto BytesIO para armazenar o PDF
    pdf_buffer = io.BytesIO()
    # Cria um objeto FPDF para o PDF
    pdf = FPDF()
    # Percorre as imagens
    for imagem in imagens:
        if imagem.filename == '':
            continue
        # Abre a imagem usando a biblioteca Pillow
        img = PILImage.open(imagem)
        # Obtém as dimensões da imagem
        img_width, img_height = img.size
        # Calcula o tamanho da página do PDF
        pdf_width = pdf.w
        pdf_height = pdf.h
        # Verifica a proporção da imagem e da página do PDF
        img_ratio = img_width / img_height
        pdf_ratio = pdf_width / pdf_height
        # Redimensiona a imagem para caber na página do PDF mantendo a proporção
        if img_ratio > pdf_ratio:
            img_width = pdf_width
            img_height = int(img_width / img_ratio)
        else:
            img_height = pdf_height
            img_width = int(img_height * img_ratio)
        # Calcula a posição para centralizar a imagem na página do PDF
        x = (pdf_width - img_width) / 2
        y = (pdf_height - img_height) / 2
        # Adiciona a imagem ao PDF
        pdf.add_page()
        caminho_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
        temp_file_path = os.path.join(caminho_downloads, 'imagem_temporaria.png')
        img.save(temp_file_path)
        pdf.image(temp_file_path, x, y, img_width, img_height)
    pdf_buffer = BytesIO()
    temp_dir = tempfile.mkdtemp()
    # Salva o PDF no buffer
    pdf_content = pdf_buffer.getvalue()
    # Define o nome do arquivo de saída
  #  output_pdf = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'imagens.pdf')
    output_pdf = os.path.join(temp_dir, 'imagens.pdf')

    # Salva o conteúdo do buffer em um arquivo
    with open(output_pdf, 'wb') as f:
        f.write(pdf_content)
    # Envia o arquivo PDF para download
    return send_file(output_pdf, as_attachment=True)
@app.route('/PDFs', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist('pdf_files')
    merger = PdfMerger()
    if files:
        try:
            for file in files:
                merger.append(file)
            output_pdf = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'conjunto.pdf')
            merger.write(output_pdf)
            merger.close()
            return send_file(output_pdf, mimetype='application/pdf', as_attachment=True, download_name='conjunto.pdf')
        except PyPDF2.errors.EmptyFileError:
            return "Nenhum arquivo PDF fornecido ou formato de arquivo não suportado"
    else:
        return "Nenhum arquivo PDF fornecido ou formato de arquivo não suportado."
@app.route('/PDFscustom', methods=['POST',"GET"])
def custom_():
    return render_template("web/custompdfs.html", title='Custom - aplha')
#def consertarisso():
def verificar_status_servidor():
    try:
        servidor_online = True  # Faça uma solicitação HEAD para o servidor
        url = request.host_url
        response = requests.get(url)
        return response.status_code == 200  # Verifique se o código de status da resposta é 200 (OK)
    except requests.exceptions.RequestException:
        return False  # Em caso de erro na solicitação, considere o servidor como offline
def listar_matriculas_logadas():
    comando = 'query session'
    resultado = subprocess.run(comando, capture_output=True, text=True)

    matriculas_logadas = []
    if resultado.returncode == 0:
        linhas = resultado.stdout.splitlines()
        for linha in linhas[1:]:
            # Usa expressão regular para extrair a matrícula da linha
            match = re.search(r'^(.*?)\s', linha)
            if match:
                matricula = match.group(1)
                matriculas_logadas.append(matricula)
                print(matricula)  # Imprime cada matrícula encontrada
    return matriculas_logadas
#pega o nome de usuario#
def get_username():
    return win32api.GetUserName()
#repensar em como utilizar melhor esse validador de login atraves do dominio.
def valida_ldap(ip_server, usu, senha):
    server = Server(ip_server, get_info=ALL)
    conn = Connection(server, user=usu, password=senha, auto_bind=AUTO_BIND_NO_TLS)
    if conn.bind():
        return True
    else:
        return False
    #dominio = ''
    #usu = input("seu usuario") + dominio
    #senha = input("sua senha")
    #ip_server = ''
    #if valida_ldap(ip_server, usu, senha):
    #    print("Usuário autenticado")
  #  else:
   #     print("Falha na autenticação")
#requerimento de logins completos.#
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return redirect('/')
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            session['matricula'] = payload['matricula']
        except jwt.ExpiredSignatureError:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function
def require_login():
    pass
sessoes = []
#Pagina de login completa#
@app.route("/", methods=["POST","GET"])
def Login():
    if request.method == 'POST':
        mycursor.execute("USE usuarios")
        Matricula = request.form.get('matricula')
        Senha = request.form.get('senha')
        # Consulta SELECT no banco de dados para recuperar o usuário correspondente
        #if Matricula in logged_users:
            #return render_template('Login.html', error='Essa conta já está sendo usada.')
        sql = "SELECT * FROM cadastrados WHERE Matricula = %s AND Senha = %s"
        mycursor.execute(sql, (Matricula, Senha))
        user = mycursor.fetchone()
        print(user)
        if user:
            mycursor.execute("UPDATE cadastrados SET tentativas = 's' WHERE Matricula = %s", (Matricula,))
            payload = {'matricula': Matricula}
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            session['token'] = token  # Armazene o token na sessão
            logged_users.add(Matricula)
            endereco_ip = socket.gethostbyname(socket.gethostname())
            nome_maquina = socket.gethostname()
            print("Endereço IP: ", endereco_ip)
            print("Nome da máquina: ", nome_maquina)
            username = get_username()
            print("Nome de usuário: ", username)
            session['matricula'] = Matricula
            return redirect("/selecao?token=" + token)
        if Matricula != user:
            return render_template('Login.html', error='Usuário ou senha inválidos')
        else:
            # Renderiza a mesma página de login novamente com uma mensagem de erro
            mycursor.execute("SELECT * FROM cadastrados WHERE Matricula = %s", (Matricula,))
            user = mycursor.fetchone()
            # Inicialize a variável de contagem de tentativas
            tentativas = 0

            # Verifique se o usuário existe
            if user is not None:
                # Obtenha o número de tentativas anteriores, se existir
                tentativas_anteriores = user[3]
                if tentativas_anteriores is not None:
                    try:
                        tentativas = int(tentativas_anteriores)
                    except ValueError:
                        # Caso a conversão falhe, defina o valor padrão
                        tentativas = 0
                # Incrementar o contador de tentativas
                tentativas += 1
                # Verificar se atingiu o limite de tentativas
                user = (user[0], user[1], user[2], tentativas)
                if tentativas >= 3:
                    if tentativas >= 4:
                        # Resetar o contador e fazer alguma ação, como bloquear a conta
                        tentativas = 0
                        return redirect('/', error='Senha apagada devido a muitas tentativas de login malsucedidas')
                    if Senha is None:
                        # Fazer alguma ação, como notificar o administrador
                        return redirect('/', error='Contate o Admin para o acesso e troca de senha!')
                # Atualizar o número de tentativas no objeto 'user'
                user[3] = tentativas
    return render_template("Login.html")
def get_foto_base64(foto):
    if foto is not None:
        foto_base64 = base64.b64encode(foto).decode('utf-8')
    else:
        with open("static/img/Icone-usuario-Png.png", "rb") as file:
            foto_padrao_bytes = file.read()
        foto_base64 = base64.b64encode(foto_padrao_bytes).decode('utf-8')
    return foto_base64
def is_admin(matricula):
    Matricula = session.get('matricula')
    mycursor.execute("USE usuarios")
    Matricula = session.get('matricula')
    sql = "SELECT Nome FROM cadastrados WHERE matricula = %s AND adm = 's' "
    user = mycursor.fetchone()
    if user:
        return True
    else:
        return False
@app.route("/selecao")
def selecao():
    mycursor.execute("USE usuarios")
    Matricula = session.get('matricula')
    print(Matricula)
    sql ="SELECT Nome FROM cadastrados WHERE matricula = %s "
    mycursor.execute(sql, (Matricula,))
    result = mycursor.fetchone()
    Nome = result[0]
    mycursor.execute("SELECT Foto FROM cadastrados WHERE matricula = %s", (Matricula,))
    foto = mycursor.fetchone()[0]
    foto_base64 = get_foto_base64(foto)
    return render_template("Seletor.html", Usuario=Nome, Foto=foto_base64,mimetype='image/jpeg',Matricula=Matricula)
@app.route("/selecao/Administracao")
@login_required
def administracao():
    Matricula = session.get('matricula')
@app.route("/Gerenciamento_financeiro", methods=["POST","GET"])
def Gerenciamento_financeiro():
    Matricula = session.get('matricula')
    return render_template ("Recursos2.html")
@app.route("/transformador", methods=["POST","GET"])
def transformador():
    mycursor.execute("USE usuarios")
    Matricula = session.get('matricula')
    print(Matricula)
    sql = "SELECT Nome FROM cadastrados WHERE matricula = %s "
    mycursor.execute(sql, (Matricula,))
    result = mycursor.fetchone()
    Nome = result[0]
    mycursor.execute("SELECT Foto FROM cadastrados WHERE matricula = %s", (Matricula,))
    foto = mycursor.fetchone()[0]
    foto_base64 = get_foto_base64(foto)
    return render_template("transformador v2.html",Usuario=Nome, Foto=foto_base64,mimetype='image/jpeg',Matricula=Matricula)
@app.route("/recursos", methods=["POST"])
def recursos():
    Matricula = session.get('matricula')
    servidor_online = verificar_status_servidor()
    sql="SELECT * FROM cadastrados WHERE Matricula = %s AND Recursos_Humanos = 's' "
    mycursor.execute(sql, (Matricula,))
    user = mycursor.fetchone()
    mycursor.execute("SELECT Nome FROM cadastrados WHERE Matricula = %s", (Matricula,))
    resultnome = mycursor.fetchone()
    nome = resultnome[0]
    if user:
        return redirect("/loading")
    else:
        session['error'] = 'Você não tem permissão de acessar. Entre em contato com o administrador para mais informações.'
        return redirect("/selecao")
@app.route("/red", methods=["POST"])
def red():
    Matricula = session.get('matricula')
    servidor_online = verificar_status_servidor()
    sql="SELECT * FROM cadastrados WHERE Matricula = %s "
    mycursor.execute(sql, (Matricula,))
    user = mycursor.fetchone()
    mycursor.execute("SELECT Nome FROM cadastrados WHERE Matricula = %s", (Matricula,))
    resultnome = mycursor.fetchone()
    nome = resultnome[0]
    if user:
        return redirect("/loadingpdf")
    else:
        session['error'] = 'Você não tem permissão de acessar. Entre em contato com o administrador para mais informações.'
        return redirect("/selecao")
#pagina de Processos completa#
@app.route("/loading")
def loading():
    return render_template("loading.html")
@app.route("/loadingpdf")
def loadingpdf():
    return render_template("loadingPDF.html")
@app.route("/att26")
def att26():
# ----------------------------------------------------------------------------------------------------------------#
    from collections import defaultdict
    Matricula = session.get('matricula')
    mycursor.execute("USE cadastro")
    mycursor.execute("CREATE TABLE IF NOT EXISTS {} (Processo VARCHAR(17), Solicitante VARCHAR(24), Observacoes VARCHAR(20), Ultimo_andamento DATE,  Documentos BLOB, PDF BLOB)".format( Matricula))
    sql = "SELECT * FROM {}".format(Matricula)
    mycursor.execute(sql)
    result = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    data = pd.DataFrame(result, columns=columns)
    if Matricula in sessoes:
        # Se já existe uma sessão para esse usuário, redireciona para a página de login
        sessoes.append(Matricula)
    mycursor.execute("USE usuarios")
    mycursor.execute("SELECT Nome FROM cadastrados WHERE Matricula = %s", (Matricula,))
    resultnome = mycursor.fetchone()
    nome = resultnome[0]
    mycursor.execute("SELECT Foto FROM cadastrados WHERE matricula = %s", (Matricula,))
    foto = mycursor.fetchone()[0]
    if foto is not None:
        foto_base64 = base64.b64encode(foto).decode('utf-8')
    else:
        with open("static/img/Icone-usuario-Png.png", "rb") as file:
            foto_padrao_bytes = file.read()
        foto_base64 = base64.b64encode(foto_padrao_bytes).decode('utf-8')
    processos_totais = 0
    Sefimpro = 0
    Asstecpro = 0
    Secgerpro = 0
    mycursor.execute("USE processos")
    mycursor.execute("SELECT COUNT(*) FROM gerênciamento_financeiro")
    result = mycursor.fetchone()
    if result:
        processos_totais = result[0]
    mycursor.execute("SELECT COUNT(*) FROM gerênciamento_financeiro WHERE Solicitante = 'SEFIM'")
    result_sefim = mycursor.fetchone()
    if result_sefim:
        Sefimpro = result_sefim[0]
    mycursor.execute("SELECT COUNT(*) FROM gerênciamento_financeiro WHERE Solicitante = 'ASSTEC'")
    result_asstec = mycursor.fetchone()
    if result_asstec:
        Asstecpro = result_asstec[0]
    mycursor.execute("SELECT COUNT(*) FROM gerênciamento_financeiro WHERE Solicitante = 'SECGER'")
    result_secger = mycursor.fetchone()
    if result_secger:
        Secgerpro = result_secger[0]
    return render_template('Recursos2.html', data=data, Usuario=nome, Foto=foto_base64, processos_totais=processos_totais,Sefimpro=Sefimpro,Asstecpro=Asstecpro,Secgerpro=Secgerpro)
#receptor de dados completo, faltando apenas reconfigurar as datas de dias.
@app.route("/att25")
def att25():
# ----------------------------------------------------------------------------------------------------------------#
    from collections import defaultdict
    Matricula = session.get('matricula')
    mycursor.execute("USE cadastro")
    mycursor.execute("CREATE TABLE IF NOT EXISTS {} (Processo VARCHAR(17), Solicitante VARCHAR(24), Observacoes VARCHAR(20), Ultimo_andamento DATE,  Documentos BLOB, PDF BLOB)".format( Matricula))
    sql = "SELECT * FROM {}".format(Matricula)
    mycursor.execute(sql)
    result = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    data = pd.DataFrame(result, columns=columns)
    if Matricula in sessoes:
        # Se já existe uma sessão para esse usuário, redireciona para a página de login
        sessoes.append(Matricula)
    mycursor.execute("USE usuarios")
    mycursor.execute("SELECT Nome FROM cadastrados WHERE Matricula = %s", (Matricula,))
    resultnome = mycursor.fetchone()
    nome = resultnome[0]
    mycursor.execute("SELECT Foto FROM cadastrados WHERE matricula = %s", (Matricula,))
    foto = mycursor.fetchone()[0]
    if foto is not None:
        foto_base64 = base64.b64encode(foto).decode('utf-8')
    else:
        with open("static/img/Icone-usuario-Png.png", "rb") as file:
            foto_padrao_bytes = file.read()
        foto_base64 = base64.b64encode(foto_padrao_bytes).decode('utf-8')
    processos_totais = 0
    Sefimpro = 0
    Asstecpro = 0
    Secgerpro = 0
    mycursor.execute("USE processos")
    mycursor.execute("SELECT COUNT(*) FROM cadastrados")
    result = mycursor.fetchone()
    if result:
        processos_totais = result[0]
    mycursor.execute("SELECT COUNT(*) FROM cadastrados WHERE Solicitante = 'SEFIM'")
    result_sefim = mycursor.fetchone()
    if result_sefim:
        Sefimpro = result_sefim[0]
    mycursor.execute("SELECT COUNT(*) FROM cadastrados WHERE Solicitante = 'ASSTEC'")
    result_asstec = mycursor.fetchone()
    if result_asstec:
        Asstecpro = result_asstec[0]
    mycursor.execute("SELECT COUNT(*) FROM cadastrados WHERE Solicitante = 'SECGER'")
    result_secger = mycursor.fetchone()
    if result_secger:
        Secgerpro = result_secger[0]
    return render_template('Recursos.html', data=data, Usuario=nome, Foto=foto_base64, processos_totais=processos_totais,Sefimpro=Sefimpro,Asstecpro=Asstecpro,Secgerpro=Secgerpro)
#receptor de dados completo, faltando apenas reconfigurar as datas de dias.
@app.route("/tableG", methods=["GET"])
def tableG():
    Matricula = session.get('matricula')
    mycursor.execute("USE cadastro")
    mycursor.execute(
        "CREATE TABLE IF NOT EXISTS {} (Processo varchar(17) ,Solicitante varchar(24) ,Observacoes varchar(20) ,Ultimo_andamento date ,Documentos blob,PDF blob)".format(Matricula))
    sql = "SELECT * FROM {}".format(Matricula)
    mycursor.execute(sql)
    result = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    data = pd.DataFrame(result, columns=columns)
    mycursor.execute("USE usuarios")
    mycursor.execute("SELECT Nome FROM cadastrados WHERE Matricula = %s", (Matricula,))
    resultnome = mycursor.fetchone()
    nome = resultnome[0]
    mycursor.execute("SELECT Foto FROM cadastrados WHERE matricula = %s", (Matricula,))
    foto = mycursor.fetchone()[0]
    foto_base64 = base64.b64encode(foto).decode('utf-8')
    return render_template("tablesG.html",data=data, Usuario=nome, Foto=foto_base64)
@app.route("/table", methods=["GET"])
def table():
    Matricula = session.get('matricula')
    mycursor.execute("USE cadastro")
    mycursor.execute(
        "CREATE TABLE IF NOT EXISTS {} (Processo varchar(17) ,Solicitante varchar(24) ,Observacoes varchar(20) ,Ultimo_andamento date ,Documentos blob,PDF blob)".format(Matricula))
    sql = "SELECT * FROM {}".format(Matricula)
    mycursor.execute(sql)
    result = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    data = pd.DataFrame(result, columns=columns)
    mycursor.execute("USE usuarios")
    mycursor.execute("SELECT Nome FROM cadastrados WHERE Matricula = %s", (Matricula,))
    resultnome = mycursor.fetchone()
    nome = resultnome[0]
    mycursor.execute("SELECT Foto FROM cadastrados WHERE matricula = %s", (Matricula,))
    foto = mycursor.fetchone()[0]
    foto_base64 = base64.b64encode(foto).decode('utf-8')
    return render_template("tables.html",data=data, Usuario=nome, Foto=foto_base64)
@app.route("/mydadosG", methods=["POST"])
def mydadosG():
   #----------------------------------------------------------------------------------------------------------------#
   Matricula = session.get('matricula')
   mycursor.execute("USE cadastro")
   Tabela = str(Matricula)
   data_atual = datetime.now()
   data_inicial = data_atual
   diferenca = data_atual - data_inicial
   Processo = request.form.get("Processo")
   Solicitante = request.form.get("Solicitante")
   Observacoes = request.form.get("Observacoes")
   Ultimo_andamento = request.form.get("Ultimo_Andamento")
   Documentos = "Null"
   PDF = "Null"
   mycursor.execute("INSERT INTO %s VALUES ('%s','%s','%s','%s','%s','%s')" % (Matricula, Processo, Solicitante, Observacoes, Ultimo_andamento, Documentos, PDF))
   mycursor.execute("USE Processos")
   mycursor.execute("INSERT INTO gerênciamento_financeiro VALUES ('%s','%s','%s','%s','%s','%s')" % (Processo, Solicitante, Observacoes, Ultimo_andamento, Documentos, PDF))
   con.commit()
   return redirect("/tableG")
@app.route("/mydados", methods=["POST"])
def mydados():
   #----------------------------------------------------------------------------------------------------------------#
   Matricula = session.get('matricula')
   mycursor.execute("USE cadastro")
   Tabela = str(Matricula)
   data_atual = datetime.now()
   data_inicial = data_atual
   diferenca = data_atual - data_inicial
   Processo = request.form.get("Processo")
   Solicitante = request.form.get("Solicitante")
   Observacoes = request.form.get("Observacoes")
   Ultimo_andamento = request.form.get("Ultimo_Andamento")
   Documentos = "Null"
   PDF = "Null"
   mycursor.execute("INSERT INTO %s VALUES ('%s','%s','%s','%s','%s','%s')" % (Matricula, Processo, Solicitante, Observacoes, Ultimo_andamento, Documentos, PDF))
   mycursor.execute("USE Processos")
   mycursor.execute("INSERT INTO cadastrados VALUES ('%s','%s','%s','%s','%s','%s')" % (Processo, Solicitante, Observacoes, Ultimo_andamento, Documentos, PDF))
   con.commit()
   return redirect("/table")
   #---------------------------------------------------------------------------------------------------------------#
@app.route('/trocar_senha', methods=["POST"])
def trocar_senha():
    Matricula = session.get('matricula')
    mycursor.execute("USE usuarios")
    Senha_atual = request.form.get("senha_atual")
    Nova_senha = request.form.get("nova_senha")
    Confirmar_senha = request.form.get("confirmar_senha")
    sql = "SELECT * FROM cadastrados WHERE Matricula = %s "
    mycursor.execute(sql, (Matricula,))
    resultado = mycursor.fetchone()
    senha_armazenada = resultado[0] if resultado else None
    if Senha_atual != senha_armazenada:
        return "Senha atual incorreta"
    if Nova_senha != Confirmar_senha:
        return "A nova senha e a confirmação de senha não coincidem"
    sql = "UPDATE cadastrados SET Senha = %s WHERE Matricula = %s"
    mycursor.execute(sql, (Nova_senha, Matricula))
    con.commit()
    return redirect("/")
#função logout
@app.route('/logout' , methods=["POST","GET"])
def logout():
    Matricula = session.get('matricula')
    if Matricula:
        session.clear()
        logged_users.discard(Matricula)  # Utilize 'discard' em vez de 'remove' para evitar o erro KeyError
    return redirect('/')
@app.route('/logout2' , methods=["POST"])
def logout2():
    Matricula = session.get('matricula')
    if Matricula:
        session.clear()
        logged_users.discard(Matricula)  # Utilize 'discard' em vez de 'remove' para evitar o erro KeyError
    return redirect('/')
@app.route('/Perfil'  , methods=["GET","POST"])
def Perfil():
    mycursor.execute("USE usuarios")
    Matricula = session.get('matricula')
    mycursor.execute("SELECT Nome FROM cadastrados WHERE Matricula = %s", (Matricula,))
    resultnome = mycursor.fetchone()
    nome = resultnome[0]
    return render_template('Perfil.html',nome=nome)
@app.route('/configperfil', methods=["POST"])
def configperfil():
    mycursor.execute("USE usuarios")
    Matricula = session.get('matricula')
    senha = request.form.get("senha")
    nome = request.form.get("nome")
    foto = request.files.get("photo")
    def salvar_foto(foto):
        try:
            sql = "UPDATE cadastrados SET Foto = %s WHERE matricula = %s"
            mycursor.execute(sql, (foto, Matricula))
            con.commit()
            print("Foto salva no banco de dados com sucesso!")
        except mysql.connector.Error as err:
            print(f"Erro ao salvar a foto: {err}")
    if senha and nome:
        sql = "UPDATE cadastrados SET senha = %s, nome = %s WHERE matricula = %s"
        mycursor.execute(sql, (senha, nome, Matricula))
        print("sucesso")

        if foto:  # Verifica se uma foto foi enviada
            foto_data = foto.read()
            salvar_foto(foto_data)
        con.commit()
    else:
        # Lida com o caso em que um ou ambos os valores estão vazios
        # Aqui você pode exibir uma mensagem de erro, redirecionar o usuário, etc.
        print("Os valores de senha ou nome estão vazios")
    return redirect("/Perfil")
@app.route('/redirecionamento', methods=["GET"])
def redirecionamento():
    Matricula = session.get('matricula')
    return redirect("/selecao")
# Função para desligar o servidor
def desligar_servidor():
    # Lógica para desligar o servidor Flask
    os.kill(os.getpid(), 9)
def agendar_desligamento():
    # Define o horário para desligamento (18:30)
    horario_desligamento = "17:00"
    # Converte a string de horário em objeto de data/hora
    horario_desligamento_obj = datetime.strptime(horario_desligamento, "%H:%M")
    # Agenda o desligamento diariamente no horário especificado
    scheduler.add_job(desligar_servidor, 'cron', hour=horario_desligamento_obj.hour, minute=horario_desligamento_obj.minute)
    # Inicia o agendamento
    scheduler.start()
print("servidor sera desligado as 17:00!!!!")
print("ATIVO")
if __name__ == '__main__':
     app.config["DEBUG"] = True
     ip_address = ""
     agendar_desligamento()
     app.run(host=ip_address)