# SOFME Installer

## Tecnologia escolhida

O instalador foi implementado com Inno Setup por ser a melhor opção para aplicações Windows desktop com:

- interface profissional e moderna;
- suporte a atalhos, menu iniciar, desinstalador e registro no Windows;
- instalação em qualquer unidade (C:, D:, E:);
- suporte a atualizações futuras;
- integração simples com executáveis PyInstaller/Windows.

## Estrutura prevista da instalação

- SOFME.exe
- DLLs e dependências
- assets/
- logs/
- Dados/
- local_params.txt

## Requisitos

- Windows 10/11
- privilégios de administrador para instalação
- espaço livre suficiente no disco

## Observação

O banco de dados e arquivos de negócio ficam na pasta Dados para preservar os dados do cliente em atualizações e desinstalações parciais.
