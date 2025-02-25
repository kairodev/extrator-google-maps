# Extrator Google Maps
Essa é uma automação simples e muito intuítiva que tem como principal objetivo buscar por um termo no Google Maps e baixar os resultados para CSV, além de pegar os resultados esse script também faz uma verificação do site do estabelecimento (quando houver) se o site tem domínio próprio, se carrega rápido, se tem SSL, As tecnologias utilizadas, e também fará uma busca por links de WhatsApp ou Instagram na página.

Atenção: Essa automação foi desenvolvida para fins de estudos apenas, não é permitido o uso para fins comerciais.

## Instalação
Instale as depêndencias do projeto
```python
pip install -r requirements.txt
```
## Uso
Para Windows
```python
python extrator.py
```
Para Linux/Mac
```python
python3 extrator.py
```

Ao iniciar o script vai ser perguntado o termo que você quer buscar (ex: Contabilidade São Paulo SP), em seguida a quantidade de resultados que você quer obter, e também vai ser perguntado se você quer capturar apenas resultados que já possuem site ou telefone.

## Como funciona?
Ao passar os dados para o script, ele vai abrir um navegador em modo invísivel com o Selenium, e então vai pegar todos links a serem consultados de acordo com a busca realizada, e então o Selenium vai acessar link por link, fazer o procedimento de análise e adicionar ao CSV.

## Resultado
![Resultado](https://i.imgur.com/lT6R9oK.png)

## Autor

- Github [@kairodev](https://www.github.com/kairodev)

