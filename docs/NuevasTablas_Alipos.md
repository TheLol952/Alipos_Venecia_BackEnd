## Aqui se llevara registro de las nuevas tablas, procedimientos, triggers o secuencias para que funcione la solucion planteada

1)-Tabla
CREATE TABLE DICCIONARIO_COMPRAS_AUTO (
    NIT VARCHAR2(20),
    NOMBRE_PROVEEDOR VARCHAR2(200),
    DIRECCION VARCHAR2(300),
    PRODUCTO VARCHAR2(500),
    CUENTA_CONTABLE VARCHAR2(100),
    TIPO_OPERACION NUMBER,
    CLASIFICACION NUMBER,
    SECTOR NUMBER,
    TIPO_COSTO_GASTO NUMBER,
    SUCURSAL VARCHAR2(100)
);

2)-Tabla
CREATE TABLE DICCIONARIO_SUCURSALES (
    ID NUMBER PRIMARY KEY,
    SUCURSAL VARCHAR2(25) NOT NULL,
    PALABRA_CLAVE VARCHAR2(250) NOT NULL
);

3)-Secuencia
CREATE SEQUENCE SEQ_DICC_SUCURSALES
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

4)-Trigger
CREATE OR REPLACE TRIGGER AutoUpdateDiccionario
AFTER INSERT OR UPDATE ON CO_COMPRAS
FOR EACH ROW
DECLARE
    -- 1) Variables para los datos del proveedor
    v_nit               TA_PROVEEDORES.NIT%TYPE;
    v_nom_proveedor     TA_PROVEEDORES.NOMBRE_PROVEEDOR%TYPE;
    v_direccion_prov    TA_PROVEEDORES.DIRECCION%TYPE;

    -- 2) Variables para los campos contables de la compra
    v_cuenta_contable   CO_COMPRAS.CUENTA_CONTABLE%TYPE;
    v_tipo_operacion    CO_COMPRAS.DTE_TIPO_OPERACION%TYPE;
    v_clasificacion     CO_COMPRAS.DTE_CLASIFICACION%TYPE;
    v_sector            CO_COMPRAS.DTE_SECTOR%TYPE;
    v_tipo_costo        CO_COMPRAS.DTE_TIPO_COSTO_GASTO%TYPE;

    -- 3) Variables para traducir CON_ENTIDAD→nombre_sucursal
    v_codigo_entidad    CO_COMPRAS.CON_ENTIDAD%TYPE;
    v_sucursal_nombre   CON_ENTIDADES.NOMBRE_CON_ENTIDAD%TYPE;

    -- 4) Variables de control
    v_prov_id           CO_COMPRAS.CDPROV%TYPE;
    v_exists            NUMBER;
BEGIN
    -----------------------------------------------------------------
    -- Paso 1: tomar el proveedor (CDPROV) de la nueva fila
    v_prov_id := :NEW.CDPROV;
    IF v_prov_id IS NULL THEN
        RETURN;  -- sin proveedor, no actualizamos diccionario
    END IF;

    -----------------------------------------------------------------
    -- Paso 2: extraer NIT, NOMBRE_PROVEEDOR y DIRECCION desde TA_PROVEEDORES
    BEGIN
        SELECT t.NIT,
               t.NOMBRE_PROVEEDOR,
               t.DIRECCION
          INTO v_nit, v_nom_proveedor, v_direccion_prov
          FROM TA_PROVEEDORES t
         WHERE t.PROVEEDOR = v_prov_id
           AND ROWNUM = 1;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RETURN;  -- si el proveedor no existe, no tiene sentido continuar
    END;

    -----------------------------------------------------------------
    -- Paso 3: tomar los campos que vienen en :NEW
    v_cuenta_contable := :NEW.CUENTA_CONTABLE;
    v_tipo_operacion  := :NEW.DTE_TIPO_OPERACION;
    v_clasificacion   := :NEW.DTE_CLASIFICACION;
    v_sector          := :NEW.DTE_SECTOR;
    v_tipo_costo      := :NEW.DTE_TIPO_COSTO_GASTO;

    -----------------------------------------------------------------
    -- Paso 4: traducir CON_ENTIDAD → NOMBRE_CON_ENTIDAD
    v_codigo_entidad := :NEW.CON_ENTIDAD;
    IF v_codigo_entidad IS NOT NULL THEN
        BEGIN
            SELECT c.NOMBRE_CON_ENTIDAD
              INTO v_sucursal_nombre
              FROM CON_ENTIDADES c
             WHERE c.CON_ENTIDAD = v_codigo_entidad
               AND ROWNUM = 1;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                v_sucursal_nombre := NULL;
        END;
    ELSE
        v_sucursal_nombre := NULL;
    END IF;

    -----------------------------------------------------------------
    -- Paso 5: verificar existencia en DICCIONARIO_COMPRAS_AUTO por NIT
    SELECT COUNT(*)
      INTO v_exists
      FROM DICCIONARIO_COMPRAS_AUTO d
     WHERE d.NIT = v_nit;

    IF v_exists > 0 THEN
        -----------------------------------------------------------------
        -- Paso 6a: actualizar la fila existente, si :NEW trae valores no null
        UPDATE DICCIONARIO_COMPRAS_AUTO d
           SET 
             -- Si :NEW.CUENTA_CONTABLE NO es NULL → lo ponemos.
             -- Si es NULL → dejamos el valor que ya había en d.CUENTA_CONTABLE.
             d.CUENTA_CONTABLE   = COALESCE(v_cuenta_contable, d.CUENTA_CONTABLE),

             d.TIPO_OPERACION    = COALESCE(v_tipo_operacion,    d.TIPO_OPERACION),
             d.CLASIFICACION     = COALESCE(v_clasificacion,     d.CLASIFICACION),
             d.SECTOR            = COALESCE(v_sector,            d.SECTOR),
             d.TIPO_COSTO_GASTO  = COALESCE(v_tipo_costo,        d.TIPO_COSTO_GASTO),

             -- Para la sucursal, si v_sucursal_nombre NO es NULL → lo dejamos;
             -- si viene NULL, no toca el valor que ya había.
             d.SUCURSAL          = COALESCE(v_sucursal_nombre,   d.SUCURSAL)

         WHERE d.NIT = v_nit;

    ELSE
        -----------------------------------------------------------------
        -- Paso 6b: insertar una fila nueva
        INSERT INTO DICCIONARIO_COMPRAS_AUTO (
            NIT,
            NOMBRE_PROVEEDOR,
            DIRECCION,
            PRODUCTO,
            CUENTA_CONTABLE,
            TIPO_OPERACION,
            CLASIFICACION,
            SECTOR,
            TIPO_COSTO_GASTO,
            SUCURSAL
        ) VALUES (
            v_nit,
            v_nom_proveedor,
            v_direccion_prov,
            NULL,                  -- producto desconocido al momento
            v_cuenta_contable,
            v_tipo_operacion,
            v_clasificacion,
            v_sector,
            v_tipo_costo,
            v_sucursal_nombre
        );
    END IF;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        -- Por seguridad, no interrumpimos la inserción/actualización en CO_COMPRAS
        NULL;
    WHEN OTHERS THEN
        -- En un trigger no queremos bloquear CO_COMPRAS:
        ROLLBACK;
END;
/

5)-Procedimiento
CREATE OR REPLACE PROCEDURE SP_INSERT_DICCIONARIO_AUTO (
    p_nit               IN VARCHAR2,
    p_nombre_proveedor  IN VARCHAR2,
    p_direccion         IN VARCHAR2,
    p_producto          IN VARCHAR2,
    p_cuenta_contable   IN VARCHAR2,
    p_tipo_operacion    IN NUMBER,
    p_clasificacion     IN NUMBER,
    p_sector            IN NUMBER,
    p_tipo_costo_gasto  IN NUMBER,
    p_sucursal          IN VARCHAR2
) AS
    v_count NUMBER;
BEGIN
    -- Verificar si ya existe ese NIT en la tabla
    SELECT COUNT(*)
      INTO v_count
      FROM DICCIONARIO_COMPRAS_AUTO
     WHERE NIT = p_nit;

    IF v_count = 0 THEN
        INSERT INTO DICCIONARIO_COMPRAS_AUTO (
            NIT,
            NOMBRE_PROVEEDOR,
            DIRECCION,
            PRODUCTO,
            CUENTA_CONTABLE,
            TIPO_OPERACION,
            CLASIFICACION,
            SECTOR,
            TIPO_COSTO_GASTO,
            SUCURSAL
        ) VALUES (
            p_nit,
            p_nombre_proveedor,
            p_direccion,
            p_producto,
            p_cuenta_contable,
            p_tipo_operacion,
            p_clasificacion,
            p_sector,
            p_tipo_costo_gasto,
            p_sucursal
        );
        COMMIT;
    END IF;
END SP_INSERT_DICCIONARIO_AUTO;
/

6)-Tabla
CREATE TABLE FACTURAS_PROCESADAS (
    CODIGO_GENERACION VARCHAR2(100) PRIMARY KEY,
    PERIODO_DECLARACION VARCHAR2(7),  -- Ej: '04/2025'
    FECHA_EMISION DATE,
    FECHA_PROCESAMIENTO DATE DEFAULT SYSDATE
);
