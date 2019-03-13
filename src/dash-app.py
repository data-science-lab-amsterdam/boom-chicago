import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import os
import flask
import re
import json
from pathlib import Path
import face_recognition
import math
import logging


logging.basicConfig(level=logging.INFO)



def get_dropdown_options(values):
    return [{'label': i, 'value': i} for i in values]


def bulma_modal(id, content=None, btn_text='OK', btn_class='is-info', active=False):
    """
    Create a modal (overlay) in bulma format
    """
    return html.Div(className='modal {}'.format('is-active' if active else ''), id='{}-modal'.format(id), children=[
        html.Div(className='modal-background'),
        html.Div(className='modal-content', children=[
            html.Div(className='box', children=[
                html.Div(className='content', children=[
                    html.Div(id='{}-modal-content'.format(id), children=content),
                    html.Button(id='{}-modal-button'.format(id),
                                className='button is-medium {}'.format(btn_class),
                                n_clicks=0,
                                children=btn_text
                                )
                ])
            ])
        ])
    ])


def bulma_dropdown(id, options):
    """
    Wrapper to create a bulma select/dropdown
    :param id: name for id of html element
    :param options: list of dicts with label and value
    :return: Dash html component
    """
    return html.Div(id=id, className='select', children=[
        html.Select([
            html.Option(value=o['value'], children=o['label']) for o in options
        ])
    ])


def bulma_columns(components, extra_classes=None):
    if extra_classes is None:
        extra_classes = ['' for _ in components]
    return html.Div(className='columns is-vcentered', children=[
        html.Div(className='column {}'.format(cls), children=[comp]) for comp, cls in zip(components, extra_classes)
    ])


def bulma_center(component):
    return html.Div(className='columns', children=[
        html.Div(className='column', children=[]),
        html.Div(className='column has-text-centered', children=[component]),
        html.Div(className='column', children=[])
    ])


def bulma_figure(url):
    return html.Figure(className="figure has-text-centered", children=[
        html.Img(src=url),
    ])


#################################

def get_result_for_starting_image(image_path):
    return {
        'path': [
            "data/images_start/Demi-2-300x300.jpg", "data/images_intermediate/Elizabeth_Berkeley_0001.jpg",
            "data/images_intermediate/Mona_Rishmawi_0001.jpg", "data/images_intermediate/Alexandra_Pelosi_0001.jpg",
            "data/images_intermediate/Catherine_Donkers_0001.jpg", "data/images_intermediate/Erin_Runnion_0001.jpg",
            "data/images_intermediate/Xiang_Huaicheng_0001.jpg"
        ],
        'similarities': [1, 2, 3, 4, 5, 6]
    }


def get_start_images():
    files = Path('./data/images_start').glob('*')

    def _get_name(path):
        return Path(path).name.split("-")[0]

    def _get_subpath(path):
        return '/'.join(str(path).split('/')[1:])

    return [(_get_subpath(filename), _get_name(filename)) for filename in files]


def render_images(num_per_row=6):
    imgs = get_start_images()
    elements = [[] for _ in range(math.ceil(len(imgs) / num_per_row))]
    for i, val in enumerate(imgs):
        url, name = val
        id = name.replace(' ', '-')
        elm = html.Div(className='column', children=[
            html.A(
                id=f'img-{url}',
                href=f'javascript:selectImage("{url}");',
                n_clicks=0,
                children=[
                    html.Figure(className='image is-128x128', children=[
                        html.Img(id=f'{url}', src=f'/images/{url}'),
                        html.Figcaption(name)
                    ])
                ]
            )
        ])
        row_num = math.floor(i / num_per_row)
        elements[row_num].append(elm)

    return [
        html.Div(className=f'columns is-{num_per_row} has-text-centered', children=row_elements) for row_elements in elements
    ]

def render_images2():
    imgs = get_start_images()
    options = [{
        'label': name,
        'value': f'<img src="/images/{url}">'
    } for url, name in imgs]
    return dcc.RadioItems(id='input-image', options=options)


app = dash.Dash()
#app.config['suppress_callback_exceptions'] = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div([

    # start images
    html.Div(className='container is-fluid', children=render_images2()),
    # Hidden div to store selected image
    html.Div(id='selected-image', style={'display': 'none'}, accessKey=''),

    # button
    html.Div(className='container is-fluid', children=[
        bulma_center(html.Button(id="btn-go", className="button is-success", n_clicks=0, children="Start matching!"))
    ]),

    html.Div(id='result-container', accessKey='{}'),

    # footer
    html.Footer(className="footer", children=[
        bulma_columns([
            bulma_figure("/images/images_app/logo-boom-chicago.png"),
            bulma_figure("/images/images_app/logo-datasciencelab.png")
        ])
    ])
])


@app.server.route('/images/<path:path>')
def serve_images(path):
    """
    Pass local images to the web server
    """
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, 'data'), path)


@app.callback(
    Output('result-container', 'accessKey'),
    [Input('btn-go', 'n_clicks')],
    [State('selected-image', 'accessKey')]
)
def start(n_clicks, input_data):
    if n_clicks is None or n_clicks == 0:
        return ''
    print(n_clicks)
    print(input_data)
    dat_in = json.loads(input_data)
    image_path = dat_in['image']

    data = get_result_for_starting_image(image_path)

    return json.dumps(data)

# @app.callback(
#     Output('image-dropdown', 'options'),
#     [Input('update-button', 'n_clicks')]
# )
# def update_source_images(_):
#     return get_image_dropdown_options()
#
#
# @app.callback(
#     Output('image', 'src'),
#     [Input('image-dropdown', 'value')]
# )
# def update_image_src(value):
#     """
#     Show the selected image
#     """
#     if value is None or value == '':
#         return '/images/controlpage/dummy.png'
#     logging.info('Selected image: {}'.format(value))
#     return os.path.join('/images/faces', value)
#
#
# @app.callback(
#     Output('cropped-image', 'src'),
#     [Input('image-dropdown', 'value')]
# )
# def update_cropped_image_src(_):
#     """
#     Show the selected image
#     """
#     return '/images/controlpage/dummy.png'
#
#
# @app.callback(
#     Output('data-container', 'accessKey'),
#     [Input('start-model-button', 'n_clicks')],
#     [State('image-dropdown', 'value')]
# )
# def choose_image(n_clicks, dropdown_value):
#     """
#     Use selected image to score model on and return estimated features
#     """
#     if n_clicks is None or n_clicks == 0:
#         return ''
#
#     logging.info('You\'ve selected "{}"'.format(dropdown_value))
#     image_file = Path(RAW_IMAGES_DIR) / dropdown_value
#
#     cropped_img_file = crop_image_to_face(image_file)
#
#     global current_image_data
#     logging.info('Start model scoring..')
#     data_raw = model_scoring.predict(cropped_img_file)
#     data = data_raw
#     data['url'] = cropped_img_file
#     data['filename'] = Path(cropped_img_file).name
#     data['features'] = {
#         x['key']: {
#             'value': x['value'],
#             'score': x['score']
#         } for x in data_raw['features']
#     }
#     current_image_data = data
#     logging.info('End model scoring')
#
#     return json.dumps(current_image_data)
#
#
# @app.callback(
#     Output('input-hair_colour', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_hair_colour(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['hair_colour']['value']
#
#
# @app.callback(
#     Output('input-hair_type', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_hair_type(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['hair_type']['value']
#
#
# @app.callback(
#     Output('input-hair_length', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_hair_length(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['hair_length']['value']
#
#
# @app.callback(
#     Output('input-gender', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_gender(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['gender']['value']
#
#
# @app.callback(
#     Output('input-glasses', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_glasses(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['glasses']['value']
#
#
# @app.callback(
#     Output('input-facial_hair', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_facial_hair(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['facial_hair']['value']
#
#
# @app.callback(
#     Output('input-hat', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_hat(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['hat']['value']
#
#
# @app.callback(
#     Output('input-tie', 'value'),
#     [Input('data-container', 'accessKey')]
# )
# def update_tie(json_string):
#     if json_string is None or json_string == '' or json_string == '{}':
#         return ''
#     data = json.loads(json_string)
#     return data['features']['tie']['value']
#
#
# @app.callback(
#     Output('end-modal', 'className'),
#     [Input('save-button', 'n_clicks')],
#     [State('input-character-name', 'value'),
#      State('input-hair_colour', 'value'),
#      State('input-hair_type', 'value'),
#      State('input-gender', 'value'),
#      State('input-glasses', 'value'),
#      State('input-hair_length', 'value'),
#      State('input-facial_hair', 'value'),
#      State('input-hat', 'value'),
#      State('input-tie', 'value')]
# )
# def save_data(n_clicks, name, f_hc, f_ht, f_ge, f_gl, f_hl, f_fh, f_h, f_t):
#     if n_clicks is None or n_clicks == 0:
#         return 'modal'
#
#     data_output = current_image_data
#     data_output['name'] = re.sub('[^\w_.)( -]', '', name)
#     data_output['features'] = {
#         'hair_colour': f_hc,
#         'hair_type': f_ht,
#         'hair_length': f_hl,
#         'gender': f_ge,
#         'glasses': f_gl,
#         'facial_hair': f_fh,
#         'hat': f_h,
#         'tie': f_t
#     }
#     try:
#         data_filepath = '{}/{}.json'.format(CHECKED_DATA_DIR, data_output['filename'])
#         logging.info("Saving data to {}".format(data_filepath))
#         with open(data_filepath, 'w') as f:
#             json.dump(data_output, f)
#     except Exception as e:
#         print(e)
#
#     return 'modal is-active'


if __name__ == '__main__':
    app.run_server(debug=True)
