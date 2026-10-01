# PuzzleCam — Gesture Capture
# PuzzleCam — Captura por Gestos

App de fotomatón controlada por gestos manuales que corre completamente en el navegador. Sin instalación, sin backend, sin dependencias que instalar.
Aplicativo de cabine de fotos controlado por gestos manuais executado diretamente no navegador. Sem instalação, sem backend, sem dependências locais a instalar.

---

## **DESCRIPCIÓN**
## **DESCRIÇÃO**

PuzzleCam captura una foto usando las manos como "marco", la convierte en un rompecabezas 3x3 con efecto fotográfico en blanco y negro, y permite armarlo usando gestos de pinch. Al completarlo, se guarda en una tira de fotos descargable.
O PuzzleCam captura uma foto usando as mãos como "moldura", converte a imagem em um quebra-cabeça 3x3 com efeito fotográfico em preto e branco estilo cabine de fotos, e permite montá-lo usando gestos de pinça. Ao completá-lo, a foto é salva em uma tirinha para download.

---

## **REQUISITOS DEL SISTEMA**
## **REQUISITOS DO SISTEMA**

- **Navegador:** Chrome o Edge (recomendado), Firefox
- **Hardware:** Cámara web
- **Conexión a internet:** Requerida para cargar el modelo de MediaPipe (~10MB, solo la primera vez)
- **Servidor local:** Requerido para ejecutar la app (no se puede abrir como archivo directamente)
- **Navegador:** Chrome ou Edge (recomendado), Firefox
- **Hardware:** Câmera web
- **Conexão com a internet:** Necessária para carregar o modelo do MediaPipe (~10MB, apenas na primeira vez)
- **Servidor local:** Necessário para executar o app (não pode ser aberto diretamente como arquivo `file://`)

---

## **INSTALACIÓN Y CONFIGURACIÓN**
## **INSTALAÇÃO E CONFIGURAÇÃO**

### 1. Clonar el repositorio
### 1. Clonar o repositório

```bash
git clone https://github.com/mishu006/Puzzle.git
cd Puzzle
```

### 2. Levantar un servidor local
### 2. Iniciar um servidor local

La app usa módulos ES y acceso a cámara, por lo que necesita correr sobre HTTP.
O app usa módulos ES e acesso à câmera, necessitando rodar via HTTP.

Instala la extensión [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) en VS Code y haz clic en **Go Live**.
Instale a extensão [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) no VS Code e clique em **Go Live**.

### 3. Abrir en el navegador
### 3. Abrir no navegador

```
http://localhost:5500
```

Permite el acceso a la cámara cuando el navegador lo solicite.
Permita o acesso à câmera quando o navegador solicitar.

---

## **ESTRUCTURA DEL PROYECTO**
## **ESTRUTURA DO PROJETO**

```
Puzzle/
├── index.html        # Punto de entrada de la app
├── app.js            # Lógica completa (tracking, puzzle, galería)
├── index.html        # Ponto de entrada do app
├── app.js            # Lógica completa (rastreamento, quebra-cabeça, galeria)
├── css/
│   └── styles.css    # Estilos y layout
│   └── styles.css    # Estilos, tema escuro e layout
└── .gitignore
```

---

## **GESTOS DE CONTROL**
## **GESTOS DE CONTROLE**

| Gesto | Acción |
| Gesto | Ação |
|---|---|
| Ambas manos haciendo pinch | Congelar el área y comenzar cuenta regresiva |
| Una mano haciendo pinch sobre una pieza | Arrastrar la pieza del puzzle |
| Puño cerrado (mantener) | Guardar puzzle completado / Reiniciar tablero |
| Ambas as mãos fazendo pinça | Congelar a área e iniciar contagem regressiva |
| Uma mão fazendo pinça sobre uma peça | Arrastar a peça do quebra-cabeça |
| Punho fechado (manter) | Salvar quebra-cabeça concluído / Reiniciar tabuleiro |

---

## **LÓGICA DE LA APLICACIÓN**
## **LÓGICA DA APLICAÇÃO**

1. Muestra ambas manos a la cámara y haz pinch para definir el recuadro de captura
2. Mantén el pinch durante la cuenta regresiva — la foto se toma automáticamente
3. La foto se divide en un puzzle 3x3 con filtro de fotomatón en blanco y negro
4. Reorganiza las piezas con gestos de pinch
5. Al completarlo, cierra el puño para guardar en la tira con animación de fragmentación
6. Descarga la tira completa cuando tengas 3 puzzles guardados
1. Mostre as duas mãos para a câmera e faça o gesto de pinça para definir a área de captura.
2. Mantenha a pinça durante a contagem regressiva — a foto será tirada automaticamente.
3. A foto é dividida em um quebra-cabeça 3x3 com filtro preto e branco.
4. Reorganize as peças usando gestos de pinça.
5. Ao concluir, feche o punho para salvar na tirinha com animação de fragmentação.
6. Baixe a tirinha completa quando tiver 3 quebra-cabeças salvos.

---

## **STACK TECNOLÓGICO**

- **[MediaPipe Tasks Vision](https://developers.google.com/mediapipe)** `v0.10.14` — detección de landmarks de la mano
- **Canvas 2D API** — renderizado, piezas del puzzle, efecto fotomatón
- **JavaScript (ES Modules)** — sin frameworks
- **CSS Custom Properties** — theming y layout
- **[MediaPipe Tasks Vision](https://developers.google.com/mediapipe)** `v0.10.14` — detecção de pontos de referência da mão (landmarks)
- **Canvas 2D API** — renderização acelerada por GPU, peças do quebra-cabeça, filtros nativos
- **JavaScript (ES Modules)** — vanilla JS, sem frameworks
- **CSS Custom Properties** — tema escuro e layout responsivo

Todas las dependencias externas se cargan por CDN. No se requiere ninguna instalación adicional.
Todas as dependências externas são carregadas via CDN.

---

## **GUIA DE SOLUCION DE PROBLEMAS**
## **GUIA DE SOLUÇÃO DE PROBLEMAS**

### **La cámara no enciende**
### **A câmera não liga**

Verifica que ninguna otra aplicación (Teams, Zoom, Discord, etc.) esté usando la cámara en segundo plano.
Verifique se nenhum outro aplicativo (Teams, Zoom, Discord, etc.) está utilizando a câmera em segundo plano.

### **La app no carga el modelo**
### **O aplicativo não carrega o modelo**

Verifica tu conexión a internet. El modelo de MediaPipe (~10MB) se descarga desde `storage.googleapis.com` y el runtime desde `cdn.jsdelivr.net`. Si alguno de esos dominios está bloqueado en tu red, la app no podrá iniciar.
Verifique sua conexão com a internet. O modelo do MediaPipe (~10MB) é baixado de `storage.googleapis.com` e o runtime de `cdn.jsdelivr.net`. Se algum desses domínios estiver bloqueado na sua rede, o app não conseguirá iniciar.

### **La app muestra pantalla negra**
### **O aplicativo exibe tela preta**

Asegúrate de estar abriendo la app desde un servidor local (HTTP), no directamente como archivo desde el explorador de archivos.
Certifique-se de estar abrindo o aplicativo a partir de um servidor local (HTTP), e não diretamente como arquivo no explorador de arquivos.

### **El gesto de pinch no se detecta**
### **O gesto de pinça não é detectado**

Asegúrate de tener buena iluminación y que ambas manos sean visibles para la cámara. Acerca más el índice y el pulgar hasta que el punto amarillo en pantalla se active.
Certifique-se de ter boa iluminação e que ambas as mãos estejam visíveis na câmera. Aproxime mais o dedo indicador do polegar até que o indicador na tela seja acionado.

---

## **COMPATIBILIDAD DE NAVEGADORES**
## **COMPATIBILIDADE DE NAVEGADORES**

| Navegador | Soporte |
| Navegador | Suporte |
|---|---|
| Chrome / Edge | Recomendado |
| Firefox | Compatible |
| Safari | Limitado (puede requerir permisos adicionales) |
| Movil | Limitado (recomendado en escritorio) |
| Firefox | Compatível |
| Safari | Limitado (pode exigir permissões adicionais) |
| Mobile | Limitado (recomendado em desktop) |

---

## **LICENCIA**
## **LICENÇA**

MIT — libre para usar, modificar y compartir.
MIT — livre para usar, modificar e compartilhar.
