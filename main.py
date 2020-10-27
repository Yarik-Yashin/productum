from flask import *
from flask_bootstrap import Bootstrap
import ocrspace
from adds import *
import os

API_KEY = '790b71df8188957'
application = Flask(__name__)
bootstrap = Bootstrap(application)
UPLOAD_FOLDER = '/files'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = ocrspace.API(api_key=API_KEY, language=ocrspace.Language.Russian)
application.config['TEMPLATES_AUTO_RELOAD'] = True


@application.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/work', methods=['GET', 'POST'])
def work():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            fish = bool(request.form.getlist('fish'))
            lakt = bool(request.form.getlist('lakt'))
            arah = bool(request.form.getlist('arah'))
            zlak = bool(request.form.getlist('zlak'))
            filename = file.filename
            file.save(filename)
            text = api.ocr_file(filename)
            os.remove(filename)
            text = text.replace('.', '').replace(',', '').replace('О', '0').split()
            print(text)
            with_adds = False
            good_results = list()
            danger_results = list()
            bad_results = list()
            for el in text:
                if el in good:
                    with_adds = True
                    good_results.append(f'{good[el]}: безопасна для человека')
                    print(good[el])
                elif el in bad:
                    with_adds = True
                    bad_results.append(f'{bad[el]}: опасна для человека')
                    print(bad[el])
                elif el in danger:
                    with_adds = True
                    danger_results.append(f'{danger[el]}: потанциально опасна для человека')
                    print(danger[el])
                elif lakt and el == 'молоко' or lakt and el == 'лактоза':
                    with_adds = True
                    danger_results.append(f'Лактоза: потанциально опасна для человека')
                elif fish and el == 'морепродукты' or lakt and el == 'рыба':
                    with_adds = True
                    danger_results.append(f'Морепродукты: потанциально опасно для человека')
                elif arah and el == 'арахис' or lakt and el == 'орехи':
                    with_adds = True
                    danger_results.append(f'Орехи: потанциально опасно для человека')
                elif zlak and el == 'злаки' or lakt and el == 'пшеница':
                    with_adds = True
                    danger_results.append(f'Злаки: потанциально опасна для человека')
            if not with_adds:
                good_results.append('На изображении добавок не обнаружено')
            good_results = list(set(good_results))
            danger_results = list(set(danger_results))
            bad_results = list(set(bad_results))
            return render_template('workpage.html',
                                   filename=filename, danger_results=danger_results, bad_results=bad_results,
                                   good_results=good_results)

    return render_template('workpage.html')


if __name__ == '__main__':
    application.run(host='0.0.0.0')
