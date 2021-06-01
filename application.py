from flask import Flask, request, render_template, redirect
from whitenoise import WhiteNoise
application = Flask(__name__)
application.wsgi_app = WhiteNoise(application.wsgi_app, root='static/')

@application.route('/')
def index():
  return render_template('test.html')

@application.route('/working')
def working():
	return "Creating the playlist"
# application.add_url_rule('/', 'working', 'working_world')

@application.route('/run')
def my_form_post():
    import testScript
    error = testScript.runScript('mr_q_5')
    if error is not None:
        return error
    return redirect('/')
    
if __name__ == '__main__':
  application.run()