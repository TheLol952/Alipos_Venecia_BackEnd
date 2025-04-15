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
    SUCURSAL VARCHAR2(100),
    FRECUENCIA NUMBER DEFAULT 1,
    ULTIMA_COMPRA DATE
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
CREATE SEQUENCE SEQ_DICC_SUCURSALES
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

5)-Procedimiento
create or replace PROCEDURE SP_INSERT_DICCIONARIO_AUTO (
    p_nit               IN VARCHAR2,
    p_nombre_proveedor IN VARCHAR2,
    p_direccion        IN VARCHAR2,
    p_producto         IN VARCHAR2,
    p_cuenta_contable  IN VARCHAR2,
    p_tipo_operacion   IN NUMBER,
    p_clasificacion    IN NUMBER,
    p_sector           IN NUMBER,
    p_tipo_costo_gasto IN NUMBER,
    p_sucursal         IN VARCHAR2
) AS
BEGIN
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
        SUCURSAL,
        FRECUENCIA,
        ULTIMA_COMPRA
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
        p_sucursal,
        1,
        SYSDATE
    );

    COMMIT;
END;

6)-Tabla
CREATE TABLE FACTURAS_PROCESADAS (
    CODIGO_GENERACION VARCHAR2(100) PRIMARY KEY,
    PERIODO_DECLARACION VARCHAR2(7),  -- Ej: '04/2025'
    FECHA_EMISION DATE,
    FECHA_PROCESAMIENTO DATE DEFAULT SYSDATE
);
