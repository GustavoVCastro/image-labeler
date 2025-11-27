# Guia de Uso - Image Labeler

Este documento fornece instruções detalhadas sobre como configurar, executar e utilizar o programa de rotulagem de imagens.

## 📋 Pré-requisitos

*   **Python 3.11** ou superior.
*   **Tkinter** (Geralmente vem instalado com o Python, mas no Linux pode ser necessário instalar separadamente: `sudo apt-get install python3-tk`).

## 🚀 Instalação e Execução

Siga os passos abaixo para preparar o ambiente e rodar o programa:

1.  **Crie um ambiente virtual (Recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/Mac
    # ou
    venv\Scripts\activate     # No Windows
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o programa:**
    ```bash
    python main.py
    ```

## 📂 Estrutura de Arquivos

O programa utiliza diretórios padrão para organizar suas imagens e etiquetas:

*   **Imagens para rotular:** Coloque suas imagens na pasta `data/images`.
    *   O programa carrega automaticamente as imagens desta pasta ao iniciar.
    *   Você também pode carregar de outra pasta usando o menu "File" -> "Open Image Directory".
*   **Etiquetas geradas:** Os arquivos de texto com as coordenadas (formato YOLO) serão salvos em `data/labels`.

## ⌨️ Atalhos de Teclado

O uso de atalhos agiliza muito o processo de rotulagem. Abaixo estão os principais comandos:

| Ação | Atalho(s) | Descrição |
| :--- | :--- | :--- |
| **Navegação** | | |
| Próxima Imagem | `Seta Direita` | Avança para a próxima imagem na sequência. |
| Imagem Anterior | `Seta Esquerda` | Retorna para a imagem anterior. |
| Voltar para Grade | `q` | Sai da visualização de edição e volta para a grade de miniaturas. |
| Rolar Grade (Cima) | `Seta Cima` | Rola a grade de miniaturas para cima. |
| Rolar Grade (Baixo) | `Seta Baixo` | Rola a grade de miniaturas para baixo. |
| **Edição** | | |
| Desfazer | `Ctrl + z` | Remove a última caixa desenhada (box). |
| Limpar Tudo | `c` | Remove **todas** as caixas da imagem atual. |
| **Zoom e Visualização** | | |
| Zoom In | `Ctrl + +` | Aumenta o zoom na imagem. |
| Zoom Out | `Ctrl + -` | Diminui o zoom na imagem. |
| Ajustar à Tela | `f` ou `Ctrl + 0` | Ajusta a imagem para caber inteiramente na janela. |
| Zoom 100% | `1` ou `Ctrl + 1` | Visualiza a imagem em tamanho real (escala 1:1). |
| Zoom 200% | `2` ou `Ctrl + 2` | Visualiza a imagem com o dobro do tamanho. |

## 💡 Dicas de Uso

1.  **Rotulagem Automática:** O programa salva automaticamente as alterações assim que você desenha uma caixa ou muda de imagem. Não é necessário apertar um botão de "Salvar".
2.  **Indicadores Visuais:** Na visão de grade (Grid View), as imagens que já possuem rótulos exibem um pequeno quadrado verde no canto inferior direito.
3.  **Formatos Suportados:** O programa suporta imagens nos formatos `.png`, `.jpg`, `.jpeg`, `.bmp` e `.gif`.
4.  **Formato de Saída:** Os arquivos de texto gerados seguem o formato YOLO:
    ```
    <class_id> <x_center> <y_center> <width> <height>
    ```
    *   Todos os valores são normalizados entre 0 e 1.
    *   `class_id` é 0 por padrão.


