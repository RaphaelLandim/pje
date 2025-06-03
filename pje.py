from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import os
from markupsafe import Markup
import time

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Use algo seguro em produção, variável ambiente é ideal

# Rotas básicas
@app.route('/')
def home():
    return render_template('home.html', current_page='home')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', current_page='sobre')

@app.route('/missa')
def missa():
    return render_template('missa.html', current_page='missa')

@app.route('/eventos')
def eventos():
    return render_template('eventos.html', current_page='eventos')

@app.route('/ministerio')
def ministerio():
    return render_template('ministerio.html', current_page='ministerio')

@app.route('/comochegar')
def comochegar():
    return render_template('comochegar.html', current_page='comochegar')

@app.route('/folheto')
def folheto():
    return render_template('folheto.html', current_page='folheto')

# Templates de banner
@app.route('/banner1')
def banner1():
    return render_template('banner/banner1/banner1.html', current_page='banner1')

@app.route('/banner4')
def banner4():
    return render_template('banner/banner4/banner4.html', current_page='banner4')


# LITURGIA DIÁRIA
@app.route('/liturgiadiaria')
def liturgiadiaria():
    data = request.args.get('data')
    if not data:
        data = datetime.now().strftime('%Y-%m-%d')

    url = f'https://www.agenciaarcanjo.com.br/api.php?tipo=liturgia&data={data}'

    MAX_RETRIES = 2  # Quantidade máxima de tentativas para a requisição
    RETRY_DELAY = 1  # segundos para aguardar entre tentativas
    TIMEOUT = 3      # segundos para timeout da requisição

    response = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            break  # Se deu certo, sai do loop
        except (requests.exceptions.RequestException) as e:
            print(f"Tentativa {attempt} falhou: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                # Todas as tentativas falharam
                response = None

    if not response:
        liturgia = {'erro': 'Não foi possível carregar a liturgia após várias tentativas.'}
        return render_template('missa/liturgiadiaria.html', liturgia=liturgia, current_page='liturgiadiaria')

    try:
        dados = response.json()

        if dados.get('erro') == 'ok':
            descricao_html = dados.get('descricao', '') or ''
            descricao2_html = dados.get('descricao2', '') or ''
            salmo_html = dados.get('salmo', '') or ''
            evangelho_html = dados.get('evangelho', '') or ''

            # Junta as descrições e parseia o HTML
            soup = BeautifulSoup(descricao_html + descricao2_html, 'html.parser')

            leituras = {}
            current_key = None
            buffer = []

            for tag in soup.find_all(['p', 'div']):
                strong_tag = tag.find('strong')
                if strong_tag:
                    # Salva leitura anterior
                    if current_key and buffer:
                        leituras[current_key] = ''.join(buffer).strip()
                        buffer = []

                    # Nova chave (título da leitura)
                    current_key = strong_tag.get_text(strip=True).replace(':', '')

                    # Remove strong e pega o resto do texto da tag
                    strong_tag.extract()
                    restante_texto = tag.get_text(strip=True)

                    # Armazena título e texto no buffer
                    buffer.append(f"<p><strong>{current_key}</strong></p>")
                    if restante_texto:
                        buffer.append(f"<p>{restante_texto}</p>")
                else:
                    if current_key:
                        buffer.append(str(tag))

            # Salva última leitura
            if current_key and buffer:
                leituras[current_key] = ''.join(buffer).strip()

            # Identifica as leituras pelo nome
            chaves_leituras = [chave for chave in leituras if 'leitura' in chave.lower()]
            primeira_leitura = leituras.get(chaves_leituras[0], '') if len(chaves_leituras) > 0 else ''
            segunda_leitura = leituras.get(chaves_leituras[1], '') if len(chaves_leituras) > 1 else ''

            liturgia = {
                'data': data,
                'primeira_leitura': primeira_leitura,
                'segunda_leitura': segunda_leitura,
                'salmo': salmo_html,
                'evangelho': evangelho_html,
            }

        else:
            liturgia = {'erro': 'Liturgia não encontrada.'}

    except Exception as e:
        print("Erro ao processar dados da liturgia:", e)
        liturgia = {'erro': 'Não foi possível processar os dados da liturgia.'}

    # Marca os valores como Markup para renderizar HTML no template
    return render_template(
        'missa/liturgiadiaria.html',
        liturgia={k: Markup(v) for k, v in liturgia.items()},
        current_page='liturgiadiaria'
    )


# Oração Eucarística
@app.route('/oeucaristica')
def oeucaristica():
    return render_template('missa/oeucaristica.html', current_page='oeucaristica')


# Contato com envio de e-mail
@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')

        corpo_email = f"""
Nome: {nome}
Telefone: {telefone}
E-mail: {email}

Mensagem:
{mensagem}
"""

        msg = MIMEText(corpo_email)
        msg['Subject'] = 'Nova mensagem do formulário de contato'
        msg['From'] = 'biratan1995@gmail.com'
        msg['To'] = 'biratan1995@gmail.com'

        try:
            # Usa 'with' para garantir fechamento do SMTP mesmo se der erro
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login('biratan1995@gmail.com', 'ohczfvjzmjlgfptl')  # senha de app - cuidado em código aberto!
                smtp.send_message(msg)

            flash('Mensagem enviada com sucesso!', 'success')
        except Exception as e:
            print(f'Erro ao enviar e-mail: {e}')
            flash(f'Erro ao enviar a mensagem: {e}', 'danger')

        return redirect(url_for('contato'))

    return render_template('contato.html', current_page='contato')


# Inicializa o servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
