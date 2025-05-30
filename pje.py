from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.mime.text import MIMEText



app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar flash messages

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

#templates de banner
@app.route('/banner1')
def banner1():
    return render_template('banner/banner1/banner1.html', current_page='banner1')

@app.route('/banner4')
def banner4():
    return render_template('banner/banner4/banner4.html', current_page='banner4')

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
        msg['From'] = 'biratan1995@gmail.com'  # seu Gmail
        msg['To'] = 'biratan1995@gmail.com'    # destinatário

        try:
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()
            smtp.login('biratan1995@gmail.com', 'ohczfvjzmjlgfptl')  # senha de app gerada
            smtp.send_message(msg)
            smtp.quit()
            flash('Mensagem enviada com sucesso!', 'success')
        except Exception as e:
            print(f'Erro: {e}')  # Mostra erro no terminal
            flash(f'Erro ao enviar a mensagem: {e}', 'danger')

        return redirect(url_for('contato'))

    return render_template('contato.html', current_page='contato')

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
