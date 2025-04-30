from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output = None
    if request.method == 'POST':
        command = request.form.get('command', '').strip()
        if command:
            try:
                # UNSAFE: Executes any command directly in shell
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                output = e.output
            except Exception as e:
                output = str(e)
    
    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)