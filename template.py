import dash
import dash_html_components as html
import dash_core_components as dcc
from datetime import datetime as dt



app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server


app.layout = html.Div(
    children=[
        html.H1("App Running"),
        html.Div(
            children=[
                html.H2('Server on 127.0.1'),
                html.P('''Generative Adversarial Networks (GANs) are one of the most interesting ideas in computer science today. Two models are trained simultaneously by an adversarial process. A generator ("the artist") learns to create images that look real, while a discriminator ("the art critic") learns to tell real images apart from fakes
                Generative Adversarial Networks (GANs) are one of the most interesting ideas in computer science today. Two models are trained simultaneously by an adversarial process. A generator ("the artist") learns to create images that look real, while a discriminator ("the art critic") learns to tell real images apart from fakes''')
            ]
        ),

        html.Div(
            className="row",
            children=[
                html.Div(
                className="four columns div-user-controls",
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.P('''Generative Adversarial Networks (GANs) are one of the most interesting ideas in computer science today. Two models are trained simultaneously by an adversarial process. A generator ("the artist") learns to create images that look real, while a discriminator ("the art critic") learns to tell real images apart from fakes
                    Generative Adversarial Networks (GANs) are one of the most interesting ideas in computer science today. Two models are trained simultaneously by an adversarial process. A generator ("the artist") learns to create images that look real, while a discriminator ("the art critic") learns to tell real images apart from fakes'''),
                    html.H5('Select Countries'),

                    html.Div(
                        className='div-for-dropdown',
                        children=[
                                dcc.DatePickerSingle(
                                    id="date-picker2",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2014, 9, 30),
                                    initial_visible_month=dt(2014, 4, 1),
                                    date=dt(2014, 4, 1).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                ),                                
                        ]
                    ),

                      html.Div(
                        className='div-for-dropdown',
                        children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2014, 9, 30),
                                    initial_visible_month=dt(2014, 4, 1),
                                    date=dt(2014, 4, 1).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                ),                                
                        ]
                    ),
                
                        ],
                    )                  
            ]
        ),
        html.Div(   
            className="eight columns div-for-charts bg-grey",             
                children=[html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className='six columns',
                            children=[dcc.Graph(), ]
                        ),
                        
                        html.Div(
                            className='six columns',
                            children=[dcc.Graph(), ]
                        ),
                    ]                    
                ),
                    html.H3("New graph below"),
                    dcc.Graph(),                   
            ]
        ),
            ],
        ),

    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8001)