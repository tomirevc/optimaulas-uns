# 🧠 OptimAulas UNS - Sistema de Optimización de Aulas

Sistema inteligente de asignación de aulas usando **Algoritmos Evolutivos** para la carrera de Ingeniería de Sistemas e Informática de la Universidad Nacional del Santa.

## 📋 Descripción

OptimAulas UNS resuelve automáticamente el problema de asignación de aulas considerando:

- **Aulas de teoría** (capacidad: 45 estudiantes)
- **Aulas de laboratorio** (capacidad: 15 estudiantes)
- **Aulas del campus** vs **Pool de aulas externas**
- **Centro de cómputo (CECOMP)** para laboratorios externos
- **Horarios disponibles** (7am-1pm, 2pm-9pm)
- **Duración de cursos** (2-4 horas)
- **Ciclos académicos**

## 🏗️ Arquitectura del Sistema

```
Frontend (Vercel)
     ↕
Backend (Google Cloud Run)
     ↕
Algoritmo Evolutivo (Python)
```

### Frontend
- **Tecnologías**: HTML5, CSS3, JavaScript, Bootstrap 5, SweetAlert2, Chart.js
- **Despliegue**: Vercel
- **Funcionalidades**: Upload de archivos, visualización de resultados, análisis estadístico

### Backend
- **Tecnologías**: Python 3.11, Flask, pandas, numpy
- **Despliegue**: Google Cloud Run (Docker)
- **Funcionalidades**: API REST, Algoritmo Genético, procesamiento de Excel

## 🚀 Despliegue Rápido

### Prerequisitos

1. **Google Cloud SDK**: [Instalar gcloud](https://cloud.google.com/sdk/docs/install)
2. **Docker**: [Instalar Docker](https://docs.docker.com/get-docker/)
3. **Node.js**: [Instalar Node.js](https://nodejs.org/)
4. **Vercel CLI**: `npm install -g vercel`

### 1. Configurar Google Cloud

```bash
# Autenticarse
gcloud auth login

# Crear proyecto (opcional)
gcloud projects create optimaulas-uns-XXXXXX
gcloud config set project optimaulas-uns-XXXXXX

# Habilitar facturación (requerido para Cloud Run)
# Hacerlo desde la consola web: https://console.cloud.google.com/billing
```

### 2. Desplegar Backend

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd optimaulas-backend

# Actualizar PROJECT_ID en deploy_gcloud.sh
nano deploy_gcloud.sh  # Cambiar "tu-proyecto-gcloud"

# Desplegar
chmod +x deploy_gcloud.sh
./deploy_gcloud.sh
```

### 3. Desplegar Frontend

```bash
cd ../optimaulas-frontend

# Descargar dependencias estáticas (Bootstrap, SweetAlert2)
# Crear directorios
mkdir -p css js

# Descargar Bootstrap
curl -o css/bootstrap.min.css https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css
curl -o js/bootstrap.bundle.min.js https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js

# Descargar SweetAlert2
curl -o css/sweetalert2.css https://cdnjs.cloudflare.com/ajax/libs/limonte-sweetalert2/11.7.12/sweetalert2.min.css
curl -o js/sweetalert2.all.min.js https://cdnjs.cloudflare.com/ajax/libs/limonte-sweetalert2/11.7.12/sweetalert2.all.min.js

# Actualizar URL del backend en index.html
nano index.html  # Cambiar API_URL con tu URL de Cloud Run

# Desplegar
chmod +x deploy_vercel.sh
./deploy_vercel.sh
```

## 🔧 Desarrollo Local

### Backend Local
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Backend disponible en: http://localhost:8080
```

### Frontend Local
```bash
cd frontend
npx serve .
# Frontend disponible en: http://localhost:3000
```

## 📊 Algoritmo Evolutivo

### Parámetros del Algoritmo
- **Población**: 50 individuos
- **Generaciones**: 100
- **Tasa de mutación**: 10%
- **Tasa de cruzamiento**: 80%
- **Selección**: Por torneo

### Función de Fitness
```python
fitness = 1000 - (conflictos × 100) - (penalización_distancia)
```

### Operadores Genéticos
1. **Cruzamiento**: Un punto de cruce
2. **Mutación**: Cambio aleatorio de aula/horario
3. **Selección**: Torneo de 3 individuos

## 📁 Estructura del Proyecto

```
optimaulas-uns/
├── backend/
│   ├── app.py                 # Aplicación Flask
│   ├── requirements.txt       # Dependencias Python
│   ├── Dockerfile            # Imagen Docker
│   ├── cloudbuild.yaml       # Config Google Cloud Build
│   ├── deploy_gcloud.sh      # Script despliegue GCP
│   └── .dockerignore         # Archivos ignorados Docker
├── frontend/
│   ├── index.html            # Interfaz principal
│   ├── vercel.json           # Configuración Vercel
│   ├── package.json          # Dependencias Node.js
│   ├── deploy_vercel.sh      # Script despliegue Vercel
│   ├── css/                  # Estilos CSS
│   │   ├── bootstrap.min.css
│   │   └── sweetalert2.css
│   └── js/                   # Scripts JavaScript
│       ├── bootstrap.bundle.min.js
│       └── sweetalert2.all.min.js
└── README.md                 # Este archivo
```

## 📋 Formato de Archivos de Entrada

### Archivo de Cursos (Excel)
| id | nombre | ciclo | tipo | estudiantes | duracion |
|----|--------|-------|------|-------------|----------|
| 1 | Algoritmos I | 3 | teoria | 40 | 2 |
| 2 | Lab Algoritmos I | 3 | laboratorio | 15 | 2 |

### Archivo de Aulas (Excel)
| id | nombre | tipo | capacidad | ubicacion | distancia |
|----|--------|------|-----------|-----------|-----------|
| A101 | Aula 101 | teoria | 45 | Campus | 0 |
| LAB01 | Laboratorio 1 | laboratorio | 15 | Campus | 0 |
| EXT01 | Aula Externa 1 | externa | 50 | Pool de Aulas | 5 |

## 📊 Salida del Sistema

### Archivo de Resultados (Excel)
- Curso asignado
- Aula asignada
- Horario optimizado
- Estadísticas de ocupación
- Métricas de calidad

### Análisis Estadístico
- Evolución del fitness por generación
- Distribución de aulas por tipo
- Conflictos detectados
- Eficiencia de la asignación

## 🐛 Troubleshooting

### Error: "gcloud command not found"
```bash
# Instalar Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### Error: "Docker daemon not running"
```bash
# Linux/Mac
sudo systemctl start docker

# Windows: Iniciar Docker Desktop
```

### Error: "vercel command not found"
```bash
npm install -g vercel
```

### Error: "Port already in use"
```bash
# Cambiar puerto en app.py
export PORT=8081
python app.py
```

## 📈 Monitoreo y Logs

### Google Cloud Run
```bash
# Ver servicios
gcloud run services list

# Ver logs
gcloud logs tail --service=optimaulas-backend

# Ver métricas
gcloud monitoring dashboards list
```

### Vercel
```bash
# Ver deployments
vercel ls

# Ver logs
vercel logs

# Ver analytics
vercel inspect
```

## 🔧 Configuración Avanzada

### Variables de Entorno Backend
- `PORT`: Puerto del servidor (default: 8080)
- `CORS_ORIGINS`: Orígenes permitidos para CORS

### Límites de Recursos Google Cloud Run
- **Memoria**: 2GB
- **CPU**: 2 vCPU
- **Timeout**: 900 segundos
- **Instancias máximas**: 10

## 📚 Referencias

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Algoritmos Evolutivos](https://en.wikipedia.org/wiki/Evolutionary_algorithm)


## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- **TM**
- **Ingeniería de Sistemas e Informática**
- **Curso de Algoritmos Evolutivos**

---
