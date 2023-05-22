import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Carregar os dados do arquivo CSV
data = pd.read_csv('population.csv')

# Obter a lista de países únicos
countries = data['Country'].unique()

# Obter os anos
population_columns = ['2022 Population', '2020 Population', '2015 Population', '2010 Population',
                      '2000 Population', '1990 Population', '1980 Population', '1970 Population']
years = [int(column.split()[0]) for column in population_columns]

# Verificar se o número de elementos é igual ao número de anos esperados
if len(population_columns) != len(years):
    raise ValueError("O número de colunas de população não corresponde ao número de anos esperados.")

# Inicializar a lista de população vazia
population = []

# Criar o aplicativo Dash
app = dash.Dash(__name__)

# Layout do aplicativo
app.layout = html.Div([
    html.Div([
        html.H2('Seleção de País'),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in countries],
            value=countries[0]
        )
    ], className='four columns'),

    html.Div([
        html.H2('Informações do País'),
        html.Div(id='country-info')
    ], className='four columns'),

    html.Div([
        html.H2('Crescimento Populacional'),
        dcc.Graph(id='population-growth-graph')
    ], className='eight columns'),

    html.Div([
        html.H2('Expectativa de Crescimento'),
        dcc.Graph(id='population-expectation-graph')
    ], className='eight columns')
], className='row')

# Atualizar as informações do país selecionado
@app.callback(
    Output('country-info', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_info(selected_country):
    country_data = data[data['Country'] == selected_country]
    capital = country_data['Capital'].iloc[0]
    density = country_data['Density (per km²)'].iloc[0]
    area = country_data['Area (km²)'].iloc[0]
    percentage = country_data['World Population Percentage'].iloc[0]

    return html.Table([
        html.Tr([html.Th('Capital'), html.Td(capital)]),
        html.Tr([html.Th('Densidade Populacional'), html.Td(density)]),
        html.Tr([html.Th('Área m2'), html.Td(area)]),
        html.Tr([html.Th('Porcentagem da População Mundial %'), html.Td(percentage)])
    ])

# Atualizar o gráfico de crescimento populacional
@app.callback(
    Output('population-growth-graph', 'figure'),
    Input('country-dropdown', 'value')
)
def update_population_growth_graph(selected_country):
    country_data = data[data['Country'] == selected_country]

    population_columns = ['2022 Population', '2020 Population', '2015 Population', '2010 Population',
                          '2000 Population', '1990 Population', '1980 Population', '1970 Population']
    population = country_data[population_columns].values.flatten()
    years = [int(column.split()[0]) for column in population_columns]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=population, mode='lines', name='População'))
    fig.update_layout(
        title=f'Crescimento Populacional de {selected_country}',
        xaxis_title='Ano',
        yaxis_title='População'
    )

    return fig

# Atualizar o gráfico de expectativa de crescimento
@app.callback(
    Output('population-expectation-graph', 'figure'),
    Input('country-dropdown', 'value')
)
def update_population_expectation_graph(selected_country):
    country_data = data[data['Country'] == selected_country]

    growth_rates = country_data['Growth Rate'].iloc[:len(years)].replace('%', '', regex=True).astype(float) / 100.0
    current_population = country_data['2022 Population'].iloc[0]
    num_years = 2050 - years[-1]

    projected_population_2050 = current_population * (1 + growth_rates.prod()) ** num_years

    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=current_population,
        number={'suffix': ' pessoas em 2022'},
        delta={'position': "top", 'reference': projected_population_2050 - current_population, 'relative': True},
        title={'text': "Expectativa em Relacao a População Atual"},

        
    ))
    fig.update_layout(
        title="Expectativa de Crescimento até 2050",
    )

    return fig


# Executar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
