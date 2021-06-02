from flask import Flask, request, render_template, redirect
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/working')
def working():
	return "Creating the playlist"

@app.route('/run')
def my_form_post():
    import script
    error = script.runScript()
    if error is not None:
        return error
    return redirect('/')
    
if __name__ == '__main__':
  app.run()