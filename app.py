from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

# @app.route('/my-link/')
# def my_link():
#   print ('Starting script')
#   import testScript
#   testScript.runScript("a")

#   # return 'Click.'
#   return index()

# @app.route('/')
# def my_form():
#     return render_template('my-form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    import testScript
    error = None
    error = testScript.runScript(text)
    if error is not None:
    	return error
    return "Creating the playlist"

if __name__ == '__main__':
  app.run(debug=True)