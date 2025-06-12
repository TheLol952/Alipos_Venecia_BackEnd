# 🧠 Buenas Prácticas para Versionamiento con Git

Este repositorio sigue una estructura organizada para facilitar el trabajo colaborativo, la trazabilidad de cambios y mantener un flujo de desarrollo limpio y profesional.

---

pyinstaller --onefile --add-data ".env;." --name FacturasDownloader main.py

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

## 🚀 Funcionalidades principales

### Diccionario para sucursales y cuentas (HECHO)
Se creara un diccionario, que este contendralo siguiente: PRODUCTO, NIT, NOMBRE_PROVEEDOR, CUENTA_CONTABLE, DIRECCION, SUCURSAL, TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO.
Donde realizara lo siguiente:
El sistema primero verificara la sucursal asociada a esa compra dentro de la tabla DICCIONARIO_SUCURSALES mediante una palabra clave asociada a dicha sucursal, en caso de no encontrar una coincidencia, lo buscara en la tabla DICCIONARIO_COMPRAS_AUTO, tomando en cuenta solamente la direccion. Mediante la direccion se concluira a que sucursal pertenece, y ambos procesos poseeran una validacion en la cual, si una palabra clave o direccion pertenece a varias sucursales mas, se concluira que este proveedor es uno de tipo servicio o comun, y la manera para concluir la sucursal perteneciente de este tipo de proveedores sera mediante la descripcion del item de compra, donde le listaran 2 tablas. 
1. Tabla CON_ENTIDADES donde se seleccionara el nombre de todas las sucursales.
2. Tabla DTE_MUNICIPIOS_013 donde se seleccionaran todos los municipios.

Luego comparara la Sucursal con el Municipio, y si el Municipio localizado en el item, concide con una de las sucursales, se tomara esa sucursal como la original, y en caso no lo logre se pondra como sucursal desconocida.

### Enlistar e insertar proveedores (HECHO)
Este proceso recibira como parametro el json de la compra y enlistara a todos los proveedores de la tabla TA_PROVEEDORES, donde se enlistara los siguientes campos: CODIGO_PROVEEDOR, NOMBRE_PROVEEDOR, DIRECCION Y NIT. Y en el caso que a la hora de insertar una compra en la db, y no se logre identificar a un proveedor (Comparando el Nit y la Direccion del proveedor en la compra y en la db), registrara a dicho proveedor en la tabla, retornando al proveedor en cuestion, ya sea 

### Enlistar e insertar productos (HECHO)
Este proceso se encargara de enlistar todos los productos en la tabla TA_PRODUCTOS, donde se enlistaran los siguientes campos: PRODUCTO(id) y NOMBRE_PRODUCTO. Y en el caso que a la hora de insertar una compra en la db, y no se logre identificar un producto (Se comprarara el nombre del producto en el json que se encuentra en 'cuerpoDocumento' en la entidad 'Descripcion' vs la columna NOMBRE_PRODUCTO) se insertara en la tabla los siguientes valores: PRODUCTO(id auto incrementable), NOMBRE_PRODUCTO, DESCRIPCION_PRODUCTO(Nombre del item), PRECIO_UNITARIO, USUARIO_CREACION(ALIPOS2025), los demas campos seran puestos como NULL.

### Formatear numero de control DTE (HECHO)
Este pequeño proceso formateara el numero de control DTE, para que en lugar de ser: DTE-03-XXXX-XXX9929
para que ahora sea asi --> 9929.

### Auto detectar la cuenta contable sobre una compra (HECHO)
Este proceso buscara asignarle una cuenta contable, segun el producto o la naturaleza de la empresa, por ejemplo si el producto es agua se intuira que la cuenta contable a la que pertenecera sera 'Agua Potable' y en el caso de que el producto sea ambiguo/nuevo/desconocido, sera por la empresa(NIT) que si por ejemplo la empresa es Texaco, se intuira que la cuenta contable sera 'Combustibles y Lubricantes', y lo hara de esta manera:
Primero se ejecutara el procedimiento que detecta la sucursal, una vez detectada la sucursal (por ej. San Martin) podra avanzar al siguiente paso.
Ahora que hemos obtenido el nombre de la sucursal, podremos relacionar a que entidad/cuenta contable pertenece, por ejemplo una cuenta contable se establece de la siguiente manera:
Primeros 2 digitos: 43 -> Se refiere al rubro principal, es este caso es al rubro GASTOS OPERATIVOS, luego se le agregan otros 2 digitos mas para saber a que cuenta contable nos estamos refiriendo, por ejemplo si es 01 nos estaremos refiriendo a la cuenta GASTOS DE VENTA, luego se le agregaran otros 2 digitos que se referira a la sucursal a la que estara ligada la cuenta, como anteriormente habiamos tomado como ejemplo San Martin, su codigo contable es (Dentro de CON_ENTIDADES -> COD_CONTABILIDAD) es 3, por lo tanto si ingresamos los digitos 03 nos estaremos refiriendo a la sucursal de San Martin, y para finalizar los ultimos 2 digitos se refiere a la sub cuenta donde se cargan los movimientos de esta por ejemplo la sub cuenta con digito 30 se refiere a la sub cuenta de 'Combustible y Lubricantes',
Dicho todo esto la cuenta contable final quedara de esta manera: 43010330.
Ahora que se ha obtenido el Nombre de la sucursal, identificaremos su CON_ENTIDAD Y COD_CONTABILIDAD de esta forma, se comparara el Nombre de la Sucursal obtenida, con la columna NOMBRE_CON_ENTIDAD en la tabla CON_ENTIDADES, donde obtendremos los valores de las columnas CON_ENTIDAD y COD_CONTABILIDAD, una vez obtenidos estos datos avanzaremos al siguiente paso.
Ahora listaremos la tabla de DICCIONARIO_COMPRAS_AUTO, para ver los datos que se han recopilado, primeramente intentara revisar la cuenta contable segun el producto, y buscara dentro del json 'cuerpoDocumento.descripcion' y lo comparara con la columna PRODUCTO, y en caso no haya registro alguno de este producto, se intentara buscar por medio del nombre de la empresa, donde en el json buscara 'emisor.nit' (el nit dentro del json esta sin guiones, y en la tabla con guiones, por lo tanto se debe formatear el json entrante para que coincida con el de la db) y lo comparara con la columna NIT, una vez identificado el producto o empresa, tomara los datos de las siguientes columnas. CUENTA_CONTABLE(En este apartado obtendremos sono unos digitos de esta columna, por ejemplo siguiendo con la misma cuenta 43010330, no obtendremos de un solo todo el valor, sino los siguientes: 4301**30, dando a entender que no asignaremos de un solo la cuenta que esta en esta columna, sino que la crearemos a partir del COD_CONTABILIDAD que obtuvimos anteriormente, para asi depurar que, en el caso de que el codigo de la columna este malo, lo asignaremos de esta manera, y la cuenta quedaria asi: 4301{COD_CONTABILIDAD}30, a esta cuenta la llamaremos cuenta_artificial, la cual sera comparada con la que esta en CUENTA_CONTABLE, y en el caso de que sean iguales, se la cuenta de la columna, pero en el caso no sean iguales, habiendo discrepancia tomara el valor de la cuenta artificial), TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO.
Una vez obtenida la cuenta contable y asignado a que sucursal pertenece, ahora verificaremos si es de tipo combustible u otras cuentas relacionadas (segun la estrucura que se muestra mas adelante), para asi asignarle la cuenta a la que esta relacionada, y lo haremos de esta forma:
Como anteriormente ya detectamos a que cuenta contable pertenece (en este caso 'Combustibles y Lubricantes') la cuenta relacionada a esta cuenta es Fovial y Cotrans, y su cuenta base y a la que se le asignara el codigo de la sucursal es la siguiente: 4301{COD_CONTABILIDAD}41 esto porque una cuenta de combustible esta ligada a los impuestos del Fovial y contrans, y esto se hara mediante un arreglo, que tendra la siguiente estructura.
[
    Cuenta_Contable: 4301xx30, 
    Nombre_Cuenta: 'Combustibles y Lubricantes',
    Cuenta_Relacionada: 4301xx41,
    Nombre_CuentaRelacionada: Fovial y Cotrans,
]
Ahora segun todos los datos anteriormente recopilados, los insertaremos en la tabla CO_COMPRAS en las siguientes columnas: CUENTA_CONTABLE, CUENTA_RELACION, CON_ENTIDAD, DTE_TIPO_OPERACION, DTE_CLASIFICACION, DTE_SECTOR, DTE_TIPO_COSTO_GASTO. 

    ## Dividimos la solucion anterior en varios archivos mas pequeñas, para su mayor escalabilidad y mantenimiento.

    ## CuentaSucursalesService.py (HECHO)
    Este servicio recibira como parametro el json de la compra, donde utilizando el diccionario de las sucursales, obtendremos el nombre de la sucursal, una vez obtenido el nombre de la sucursal obtendremos la entidad y el codigo contable de la sucursal de la siguiente manera:
    Con el nombre de la sucursal buscaremos la sucursal que conicida en la tabla de CON_ENTIDADES la columna NOMBRE_CON_ENTIDAD, una vez identificado, obtendremos los datos de las columnas CON_ENTIDAD y COD_CONTABILIDAD.
    Finalmente retornando estos datos: NombreSucursal, ConEntidad y CodContabilidad.

    ## CuentaBaseService.py (HECHO)
    Este servicio recibira como parametro el json de la compra, donde sacara del json los siguientes datos:
    descripcionProducto -> cuerpoDocumento.descripcion,
    nitEmpresa -> emisor.nit
    Donde realizara lo siguiente: Si el producto en la compra es uno solo y esta registrado en DICCIONARIO_COMPRAS_AUTO comparara descripcionProducto con la columna PRODUCTO, y obtendra,
    NOMBRE_CUENTA, CUENTA_CONTABLE(Aqui obtendremos solo la cuenta base, que por ejemplo si la cuenta es 43010411 solamente se devolvera asi 4301xx11), TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO, y si hay mas de un producto o el producto sea desconocido, intentara comparar nitEmpresa con la columna NIT(se debera de formatear el nit, porque viene sin guiones)... donde el procedimiento retornara con los siguientes nombres, CuentaBase, TipoOperacion, Clasificacion, Sector y TipoCostoGasto.

    ## CuentaFinalService.py (HECHO)
    Este servicio recibira como parametro la CuentaBase y el CodContabilidad, y este servicio sera el encargado de formar la cuenta final, donde se formara de la siguiente manera:
    pasara de 4301xx11 -> 4301{CodContabilidad}11 guardandose en la variable CuentaFinal, una vez obtenida la cuenta final, ahora pasaremos a las cuentas relacionadas, donde por medio de un mini diccionario que almacena las cuentas y si tiene relacion con alguna otra como por ejemplo:
    [
    Cuenta_Contable: 4301xx30, 
    Nombre_Cuenta: 'Combustibles y Lubricantes',
    Cuenta_Relacionada: 4301xx41,
    Nombre_CuentaRelacionada: Fovial y Cotrans,
    ]   
    donde sustituira las 'xx' por el codigo de contabilidad, donde el procedimiento al final retornara lo siguiente: CuentaFinal y CuentaRelacionada

    ## AutoCuentaContable.py (HECHO)
    Este procedimiento al ser llamado ejecutara y llamara a los anteriores archivos creados y los datos retornados los guardara en variables que se utilizaran mas adelante, primero se ejecutara el archivo
    CuentaSucursalesService.py, luego CuentaBaseService.py y finalmente CuentaFinalService.py y ahora que hemos obtenido y guardado todos los datos necesarios, los insertaremos en nuesta db en la tabla, pero eso lo haremos en otro procedimiento, por el momento soalemte retornaremos los datos: CUENTA_CONTABLE, CUENTA_RELACION, CON_ENTIDAD, DTE_TIPO_OPERACION, DTE_CLASIFICACION, DTE_SECTOR, DTE_TIPO_COSTO_GASTO.

### Insertar productos en DETCOMPRAS (HECHO)
Este proceso se encargara de insertar todos los items dentro de una compra, hacia la tabla CO_DETCOMPRAS donde se deberan de ingresar los siguientes campos: ID(auto), CODEEMP(ALIPOS2025), CODPROV(Codigo del proveedor 'Nit' segun la compra original formateada), TIPO(Segun compra, que esta por defecto 1), COMPROB(Es el correlativo de la compra original, que es el numero de controls DTE pero formateado), CANTIDAD, PRECIOU, TOT(Total), IDPRODUCTO(Es el id del producto, se utilizara el proceso 3), CORRE_COMPRA(es el id de la compra 'CORRE', que se pondra x veces segun el N de items), PARA_INVENTARIO(Si el item se enviara para inventario, su valor sera 1, sino su valor por defecto sera 0), CUENTA_CONTABLE(Es la cuenta contable que heredara de la compra), EXCENTA(Por defecto, su valor sera 0).

### Verificar si es combustible (HECHO)
Este proceso recibira como parametro el archivo json y verificara si la compra posee estos 2 elementos en "cuerpoDocumento" dentro del atributo "tributos" en los cuales estaran 2 codigos, siendo "D1" para el Fovial, y "C8" para el Cotrans, luego en "resumen" deberan estar ambos detallados conteniendo:
{
    codigo: D1,
    descripcion: 'Fovial',
    valor: 2.34
}
y
{
    codigo: C8,
    descripcion: 'Cotrans',
    valor: 1.08
}
ambos valores seran almacenados en las columnas FOVIAL Y COTRANS, y en este caso se deduce que la compra realizada es combustible, por lo tanto se marcara  ES_COMBUSTIBLE(1), el valor por defecto sera de 0 hasta que se demuestre que la compra es de tipo combustible.
El procedimiento Retornara los siguientes valores: ES_COMBUSTIBLE, FOVIAL(valor) Y COTRANS(valor)

### Obtener los datos de una compra (json) (HECHO)
Este proceso recibira como parametro el archivo json y revisara que posea estos atributos:
CODTIPO(En los archivos json hay un atributo llamado 'tipoDte' que tiene un valor, dicho valor se comparara con la tabla DTE_TIPO_DOCUMENTO_002, y comparara la columna CODIGO_MH y extraera el valor con el que coincidio), COMPROB(Sera el correlativo del numero de control sin guiones ni ceros, por ejemplo: 8207, se utilizara el proceso 4), FECHA(Es la fecha de emision de la factura), COMPRAIE(Se pondra en 0, ya que no se reciben compras excentas en digital), COMPRAEE(Similar al caso anterior, se pondra en 0), COMPRAIG(Se tomara este valor de 'resumen.totalGravada', que es el subtotal de la compra), IVA(Se tomara de 'resumen.tributos[codigo:20, valor:(13%)]' que sera el 13% del subtotal), TOTALCOMP(Es la sumatoria del subtotal + iva, o se puede tomar de 'totalPagar'), RETENCION(Se aplica el 1% sobre el subtotal, o se toma de 'resumen.ivaRete1'), DESCUENTOS(Es el total de los descuentos de la compra, se tomara de 'resumen.totalDescu'), IVA_PERCIBIDO(Se aplica el 1% sobre el subtotal, o se toma directamente de 'resumen.ivaPerci1').

### Actualizar la tabla de DICCIONARIO_COMPRAS_AUTO

## Insertar a tabla cuando se haya insertado una compra y un detalle de compra

6)-Tabla
CREATE TABLE FACTURAS_PROCESADAS (
    CODIGO_GENERACION VARCHAR2(100) PRIMARY KEY,
    PERIODO_DECLARACION VARCHAR2(7),  -- Ej: '04/2025'
    FECHA_EMISION DATE,
    FECHA_PROCESAMIENTO DATE DEFAULT SYSDATE
);