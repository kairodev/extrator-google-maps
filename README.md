# Extrator Google Maps

![Extrator Google Maps](https://ibb.co/QFSRq0nP) <!-- Adicione o link da imagem aqui -->

**Extrator Google Maps** é uma automação simples e intuitiva que busca por um termo no Google Maps e baixa os resultados em formato CSV. Além de coletar os resultados, este script verifica o site do estabelecimento (quando disponível), analisando se o site possui domínio próprio, a velocidade de carregamento, se possui SSL, as tecnologias utilizadas e busca por links de WhatsApp ou Instagram na página.

**Atenção**: Esta automação foi desenvolvida apenas para fins de estudo; o uso comercial não é permitido.

## Instalação

Instale as dependências do projeto:

```bash
pip install -r requirements.txt

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

## Exemplo de Saída

Os dados extraídos serão salvos em um arquivo CSV com as seguintes colunas:

Nome
Endereço
Telefone
Site
Reputação
Site Próprio
Velocidade de Carregamento
Tem SSL
Domínio
WhatsApp
Instagram
Tecnologias

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um issue ou criar um pull request.

## Licença
Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.

## Autor

- Github [@kairodev](https://www.github.com/kairodev)
