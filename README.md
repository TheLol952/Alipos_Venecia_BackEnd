# 🧠 Buenas Prácticas para Versionamiento con Git

Este repositorio sigue una estructura organizada para facilitar el trabajo colaborativo, la trazabilidad de cambios y mantener un flujo de desarrollo limpio y profesional.

---

## 📌 Estructura de Ramas

### Ramas principales:

- `main` → Rama estable para producción
- `Developing` → Rama de integración para pruebas y nuevas funcionalidades

### Ramas temporales:

Cada cambio, función o arreglo debe desarrollarse en su **propia rama** a partir de `Developing`.

#### 🔧 Convención de nombres:

tipo/nombre-descriptivo/autor/fecha

> Usa solo letras minúsculas y `-` como separador entre palabras.

#### Ejemplos:

- `feature/nueva-funcion-identificar-sucursal/josue/2025-04-15`
- `bugfix/corrige-conexion-db/josue`
- `hotfix/arreglo-produccion-conexion`

---

## ✅ Tipos de ramas

| Tipo      | Prefijo    | Uso                                               |
|-----------|------------|----------------------------------------------------|
| Feature   | `feature/` | Nuevas funcionalidades                             |
| Bugfix    | `bugfix/`  | Corrección de errores detectados                   |
| Hotfix    | `hotfix/`  | Correcciones urgentes en producción (`main`)      |
| Chore     | `chore/`   | Tareas menores, refactors, cambios en configuración|

---

## ✍️ Convención de Commits

Utiliza [Conventional Commits](https://www.conventionalcommits.org) para mantener un historial claro y consistente.

### 📦 Ejemplos:

```bash
feat: agrega nueva lógica para identificar sucursales
fix: corrige error en la conexión a Oracle DB
refactor: organiza el módulo de conexión
chore: actualiza dependencias y .env de ejemplo

📌 Prefijos comunes:

Tipo	Descripción
feat	Nueva funcionalidad
fix	Corrección de errores
refactor	Cambio de estructura sin afectar funcionalidad
chore	Mantenimiento (dependencias, configs, etc.)
docs	Cambios en documentación
test	Agregado o mejora de pruebas
