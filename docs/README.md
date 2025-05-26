##  Para instalar las dependencias del proyecto:
'pip install -r requirements.txt'

## Activar entorno virtual
'.\venv\Scripts\activate'

## Correr archivos, por ejemplo
'python .\src\procedimientos\DiccionarioSucursales.py'

## Importa la db.DMP a Oracle sql
'impdp ALIPOS/ALIPOS2025 DIRECTORY=dmp_dir DUMPFILE=ALIPOS_db.DMP LOGFILE=retry_import.log'

##  Para importar exitosamente la db de ALIPOS
CREATE TABLESPACE TANGO23
DATAFILE 'C:\oraclexe\app\oracle\oradata\XE\TANGO23.dbf' 
SIZE 100M 
AUTOEXTEND ON 
NEXT 10M MAXSIZE UNLIMITED;

CREATE TABLESPACE TANGO23_TOLEDOMAZA
DATAFILE 'C:\oraclexe\app\oracle\oradata\XE\TANGO23_TOLEDOMAZA.dbf'
SIZE 100M AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;

CREATE TABLESPACE ALIPOS
DATAFILE 'C:\oraclexe\app\oracle\oradata\XE\ALIPOS.dbf'
SIZE 100M
AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;

## Comprobar Tablespace que hay en la db u objetos invalidos
SELECT object_name, object_type, status
FROM all_objects
WHERE owner = 'ALIPOS' AND status = 'INVALID';

SELECT table_name
FROM all_tables
WHERE owner = 'ALIPOS'
ORDER BY table_name;

##  Eliminar Tablespace
DROP TABLESPACE TANGO23 INCLUDING CONTENTS AND DATAFILES;
DROP TABLESPACE TANGO23_TOLEDOMAZA INCLUDING CONTENTS AND DATAFILES;
DROP TABLESPACE ALIPOS INCLUDING CONTENTS AND DATAFILES;

## Consulta para mostrar el Nit, Proveedor, Direccion, Nombre Producto, Nombre Cuenta, Cuenta contable, Tipo operacion, Clasificacion, Sector, Tipo Costo Gasto y Sucursal.

SELECT
    TP.NIT,
    TP.NOMBRE_PROVEEDOR,
    TP.DIRECCION,
    P.NOMBRE_PRODUCTO AS PRODUCTO,
    CC.NOMBRE_CUENTA AS NOMBRE_CUENTA,
    CC.CUENTA_CONTABLE AS CUENTA_CONTABLE,
    CC.DTE_TIPO_OPERACION AS TIPO_OPERACION,
    CC.DTE_CLASIFICACION AS CLASIFICACION,
    CC.DTE_SECTOR AS SECTOR,
    CC.DTE_TIPO_COSTO_GASTO AS TIPO_COSTO_GASTO,
    CE.NOMBRE_CON_ENTIDAD AS SUCURSAL
FROM ALIPOS.CO_COMPRAS C
JOIN ALIPOS.CO_DETCOMPRA DC ON DC.CORRE_COMPRA = C.CORRE
JOIN ALIPOS.TA_PROVEEDORES TP ON TP.PROVEEDOR = C.CDPROV
JOIN ALIPOS.TA_PRODUCTOS P ON P.PRODUCTO = DC.IDPRODUCTO
LEFT JOIN ALIPOS.CON_CATALOGO CC ON CC.CUENTA_CONTABLE = C.CUENTA_CONTABLE
LEFT JOIN ALIPOS.CON_ENTIDADES CE ON CE.CON_ENTIDAD = C.CON_ENTIDAD
WHERE TP.NIT IS NOT NULL 
  AND CE.NOMBRE_CON_ENTIDAD IS NOT NULL 
  AND CC.NOMBRE_CUENTA IS NOT NULL 

## Taba para el diccionario de compras
CREATE TABLE DICCIONARIO_COMPRAS_AUTO (
    NIT VARCHAR2(20),
    NOMBRE_PROVEEDOR VARCHAR2(200),
    DIRECCION VARCHAR2(300),
    PRODUCTO VARCHAR2(500),
    NOMBRE_CUENTA VARCHAR2(100),
    CUENTA_CONTABLE NUMBER,
    TIPO_OPERACION NUMBER,
    CLASIFICACION NUMBER,
    SECTOR NUMBER,
    TIPO_COSTO_GASTO NUMBER,
    SUCURSAL VARCHAR2(100),
    FRECUENCIA NUMBER DEFAULT 1,
    ULTIMA_COMPRA DATE
);

## Tabla para el diccionario de sucursales, esta tendra por objetivo identificar palabras clave que se le atribuyen a una sucursal, por ejemplo si en una direccion hace mencion a San Miguel, tomara en cuenta esa direecion clave, y a la hora que se encuentre con mas facturas con esa direccion, se asumira que dicha compra le pertenece a San Miguel
-- 1. Tabla
CREATE TABLE DICCIONARIO_SUCURSALES (
    ID NUMBER PRIMARY KEY,
    SUCURSAL VARCHAR2(100) NOT NULL,
    PALABRA_CLAVE VARCHAR2(200) NOT NULL
);

-- 2. Secuencia
CREATE SEQUENCE SEQ_DICC_SUCURSALES
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

-- 3. Trigger
CREATE SEQUENCE SEQ_DICC_SUCURSALES
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

## Procedimiento Almacenado
CREATE OR REPLACE PROCEDURE SP_INSERT_DICCIONARIO_AUTO (
    p_nit               IN VARCHAR2,
    p_nombre_proveedor IN VARCHAR2,
    p_direccion        IN VARCHAR2,
    p_producto         IN VARCHAR2,
    p_nombre_cuenta    IN VARCHAR2,
    p_cuenta_contable  IN NUMBER,
    p_tipo_operacion   IN NUMBER,
    p_clasificacion    IN NUMBER,
    p_sector           IN NUMBER,
    p_tipo_costo_gasto IN NUMBER,
    p_sucursal         IN VARCHAR2
) AS
    v_count NUMBER;
BEGIN
    -- Validar que el NIT tenga exactamente 17 caracteres
    IF LENGTH(p_nit) != 17 THEN
        RAISE_APPLICATION_ERROR(-20001, 'El NIT debe tener exactamente 17 caracteres. NIT proporcionado: ' || p_nit);
    END IF;

    -- Verificar si el registro ya existe
    SELECT COUNT(*)
    INTO v_count
    FROM DICCIONARIO_COMPRAS_AUTO
      WHERE NIT = p_nit
      AND PRODUCTO = p_producto
      AND CUENTA_CONTABLE = p_cuenta_contable
      AND TIPO_OPERACION = p_tipo_operacion
      AND CLASIFICACION = p_clasificacion
      AND SECTOR = p_sector
      AND TIPO_COSTO_GASTO = p_tipo_costo_gasto
      AND SUCURSAL = p_sucursal;

    -- Insertar solo si no existe
    IF v_count = 0 THEN
        INSERT INTO DICCIONARIO_COMPRAS_AUTO (
            NIT,
            NOMBRE_PROVEEDOR,
            DIRECCION,
            PRODUCTO,
            NOMBRE_CUENTA,
            CUENTA_CONTABLE,
            TIPO_OPERACION,
            CLASIFICACION,
            SECTOR,
            TIPO_COSTO_GASTO,
            SUCURSAL,
            FRECUENCIA,
            ULTIMA_COMPRA
        ) VALUES (
            p_nit,
            p_nombre_proveedor,
            p_direccion,
            p_producto,
            p_nombre_cuenta,
            p_cuenta_contable,
            p_tipo_operacion,
            p_clasificacion,
            p_sector,
            p_tipo_costo_gasto,
            p_sucursal,
            1,
            SYSDATE
        );

        COMMIT;
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;

## Ejemplo Proceso almacenado
BEGIN
    SP_INSERT_DICCIONARIO_AUTO(
        '06140107911039',
        'COMPAÑIA SALVADOREÑA DE SEGURIDAD, S.A. DE C.V.',
        'COLONIA Y AVENIDA BERNAL, RESIDENCIAL MONTECARMELO No. 21',
        'SERVICIO DE VIGILANCIA',
        '6112-004',
        1,
        2,
        2,
        1,
        'BOULEVARD CONSTITUCION'
    );
END;
/
