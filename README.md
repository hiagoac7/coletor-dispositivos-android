# Coletor de Dispositivos Android

Aplicativo em Python e Kivy para coletar fabricante, modelo, serial disponível, versão do Android e Android ID, associar o aparelho a um usuário e enviar os dados a uma planilha Google Sheets por um Web App do Google Apps Script.

Projeto separado de [Inventário de Ativos de TI — Windows](https://github.com/hiagoac7/inventario-ti).

## Tecnologias

Python, Kivy, PyJNIus, Buildozer, Android SDK/NDK e integração HTTP com Google Apps Script. O código do servidor Apps Script não está incluído.

## Configuração

1. Copie `config.example.json` para `config.json`.
2. Informe a URL HTTPS do seu Web App do Apps Script e os usuários autorizados.
3. Configure e revise o endpoint antes de compilar. Ele deve receber um POST com campos de formulário `usuario`, `fabricante`, `modelo`, `serial`, `android` e `imei`.
4. Compile em Linux com o ambiente do Buildozer e suas dependências Android: `buildozer android debug`. O APK ficará em `bin/`. Alternativamente use o notebook auxiliar.

O campo legado `imei` transporta o **Android ID**, não o IMEI. Isso preserva o contrato do cliente original. O serial pode estar indisponível ou retornar um identificador de build em versões recentes do Android; não o trate como identificador único confiável. Fora do Android, o aplicativo usa dados fictícios para demonstração.

## Segurança e privacidade

A lista nominal e o endpoint original foram retirados desta versão. `config.json` fica fora do Git, mas é incluído no APK durante a compilação: não coloque senhas ou segredos nele. Restrinja acesso no servidor e colete somente os dados necessários, com autorização dos envolvidos. A conexão usa a verificação padrão de certificados TLS.

O retorno do servidor ainda usa o comportamento legado: respostas contendo "Erro" são falhas; outras respostas são exibidas como sucesso. Ajuste esse contrato com o servidor antes do uso em produção.

## Validação

A separação e a sintaxe Python foram verificadas. A compilação do APK, a compatibilidade do ambiente de build e o envio real ao Google Sheets precisam de testes no ambiente de destino. Não há APK validado anexado a este repositório.

## Arquivos

- `main.py`: interface, coleta e envio.
- `buildozer.spec`: configuração do APK.
- `config.example.json`: exemplo sem dados reais.
- `Build_APK_Colab.ipynb`: notebook auxiliar que baixa este repositório, solicita a configuração local e inicia o build.
