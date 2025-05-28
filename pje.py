from flask import Flask, render_template, request

app = Flask(__name__)

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

@app.route('/contato')
def contato():
    return render_template('contato.html', current_page='contato')

# ... demais rotas com current_page adequado

if __name__ == '__main__':
    app.run(debug=True)
