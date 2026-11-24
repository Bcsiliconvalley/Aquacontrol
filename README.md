💧 AquaControl — Agua del Valle S.A. de C.V.
Sistema de Gestión y Monitoreo Inteligente del Agua diseñado para reducir en un 30% el agua extraída y el agua perdida en 3 años, detectar fugas de forma temprana, activar sistemas de captación pluvial y reutilización, y generar evidencia para auditorías ISO 14001 y NOM.
🚀 Instalación y Ejecución
1. Instalar dependencias:
2. pip install -r requirements.txt
3. Iniciar la aplicación:
4. streamlit run app.py
⚠️ Nota Importante para el Equipo: Archivo users_aquacontrol.json
Este proyecto utiliza el archivo users_aquacontrol.json como base de datos local para gestionar el inicio de sesión, las contraseñas encriptadas y los roles (Administrador, Área Ambiental, Operador).
🔑 Credenciales de prueba (por defecto)
- Administrador: Usuario: admin | Contraseña: 123
- Operador: Usuario: operador1 | Contraseña: 456
- Área Ambiental: Usuario: ambiental1 | Contraseña: 789
🧪 ¿Cómo probar el registro y los roles?
En la pantalla de inicio de sesión, ve a la pestaña "Registrarse". Puedes crear un usuario nuevo y seleccionar el rol de "Operador". Al hacerlo, notarás que el menú lateral se adapta y oculta las opciones administrativas y de auditoría (Reportes ISO 14001 y Capacitación y Config.), dejando visibles únicamente los módulos operativos de campo (Dashboard y 6 KPIs, Captura Diaria F-1, Alertas y Prevención F-2 y Mapa de Sectores).
☁️ Nota sobre el estado del archivo en Streamlit Cloud
Dado que este proyecto puede desplegarse en Streamlit Cloud y los archivos locales (users_aquacontrol.json y los registros .csv) viven en el entorno del repositorio, si la app se reinicia o entra en suspensión, los usuarios nuevos que se registren y las lecturas capturadas podrían borrarse y el archivo volverá a su estado original (con los tres usuarios de prueba). Esto es normal en esta versión de demostración. Si deseas guardar los usuarios y registros de forma permanente, se recomienda no subir users_aquacontrol.json al repositorio público y conectar una base de datos externa en el futuro.
