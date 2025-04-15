## COMO SE RELLENARIA SEGUN LA TABLA CO_COMPRAS
*CORRE --> Id auto incrementable
*CODEEMP --> Codigo/Nombre del usuario
*CODTIPO --> Tipo de factura, por ej CCF o FAC
*COMPROB --> Correlativo de la factura(puede ser el codigo de generacion)
*FECHA --> Fecha de emision de la factura
*COMPRAIE --> SubTotal de Compra Interna Excenta
*COMPRAEE --> SubTotal de Compra Externa Excenta
*COMPRAIG --> SubTotal de Compra Interna Gravada
*EXPORTACIO --> SubTotal de Compras Importadas Internacionalmente
*IVA --> Impuesto al Valor Agregado 13%
*TOTALCOMP --> Es el total de la compra (Con todos los subtotales e impuestos deducidos)
*RETENCION --> Es el impuesto del 1%
*RETENCIONIVA --> (No se usa)
*ANTICIPO --> ???
*MESD --> Mes tributario al que se declarara
*ANOD --> Año tributario al que se declarara
*COMPRAEXC --> Compras Exentas
*FECHADIG --> Fecha en la que fue digitada la compra (en este contexto, la fecha en la que fue descargada la factura)
*COMPRET --> Numero de serie de la compra (En el caso que sea factura fisica)
*CDPROV --> Codigo del proveedor?
*DAI --> Es el impuesto al Derecho Arancelario a la Importacion, sobre las importaciones
*IVAADUANA --> Es el IVA que cobra la Aduana
*TIPOPOLIZA --> Es el Tipo de Poliza que puede haber
*POLIZA --> Es el N o Correlativo de la poliza a la compra
*DESCUENTOS --> Es el total de los descuentos que puede poseer una compra
*CERRADO --> Mira si la operacion de la compra ha sido cerrada?
*TIPO_COMPRA --> Mira que tipo de compra es (1: Compras Internas, 2: Compras Importadas, 
3: Compras Internas Excentas sin iva)
*ID_TIPOCOMPRA --> Es el id, de que tipo de compra es segun TA_TIPO_COMPRA (1: Gasto, 2: Consumo Interno, 3: Compra Inventario, 4: Compra Exenta)
*CORRELATIVO_DTE --> Se refiere al correlativo Real que tuviera la factura digital, si estuviera en fisico, por ej.
DTE-03-01010723-000000000054775 --> 000000000054775 (se elimina "DTE-03-01010723")
*NUMERO_CONTROL_DTE --> Se refiere al N de control de una factura electronica. ej anterior
*SELLO_RECIBIDO_DTE --> Se refiere a la respuesta que manda hacienda sobre la factura, que significa que dicha factura ha sido recibida y autorizada por hacienda
*ID_TIPO_COMPRA_O --> Se refiere al tipo de compra que es originalmente (1: Compras Internacional, 2: Compra Centroamericana, 3: Compra Interna, 4: Compra Exenta) segun TA_TIPO_COMRA_ORIGEN
##En este apartado, el sistema automatizado sacara los valores segun los datos que el json tenga, y si posee los 2 (Fovial y Contrans) se pondra automaticamente con valor de 1 la columna "ES_COMBUSTIBLE"
*ES_COMBUSTIBLE --> Se refiere a que si la compra es de tipo Gasolina (tiene Fovial y Cotrans) 0: NO, 1: SI
*FOVIAL --> Es el impuesto Fovial sobre combustible
*CONTRANS --> Es el Impuesto Cotrans sobre combustible
*CODIGO_GENERACION_DTE --> Es el "id" de una Factura electronica, en base a este valor, se renombran los Json y Pdf descargados por el proceso
*IVA_PERCIBIDO --> Es el impuesto percibido por el 1% del subtotal de la compra, esto cuando el proveedor es Gran Contribuyente
*CUENTA_CONTABLE --> Es la cuenta que se le asigna a una compra segun su naturaleza 
(por ej. Cta: 41020101 Donde: 4102 -> Compra de Mercaderia, 01 -> Compras Nacionales, 01 -> Sucursal Centro)
*CUENTA_RELACION --> (No se usa)
*HORA --> Hora en la que fue procesada la compra (segun sistema automatizado)
*CON_ENTIDAD --> Se refiere al codigo interno que pertenece a cada sucursal segun la db 
(por ejemplo 06: San Miguel, 03: Tonacatepeque, 05: San Martin, etc.)
*BLOQUEF_EXCENTAS --> Es el bloque de facturas que pertenecen a facturas excentas (solo facturas fisicas, por ejemplo: 22SD003C)
*FECHA_FACTURACION_HORA --> Fecha y Hora en la que la compra fue procesada (segun la automatizacion)
*RETENCION_2PORCIENTO --> Similar a la retencion, soloq eu con 2% de deduccion
*COMENTARIO --> Comentarios extra que el usuario crea necesarios sobre dicha factura
*ADUANA --> Se refiere al id interno de la aduana, por ej. 01: Terrestre San Bartolo
*PROVEEDOR_EXT --> Se refiere al id interno de un proveedor externo, por ej. 01: BEIJIN WM INPORT AND EXPORT CO, LTD, CHINA
*CODIGO_IMPORTACION --> Es el correlativo o id de la compra internacional que se ha realizado
*CONCEPTO_COMPRA --> Se refiere a que concepto o el porque se esta realizando la compra, (por ej. 1: Importacion, 2: Internacion, 3: Importacion de Servicios)
*CODIGO_CORRE_FACTURA --> Este es el Codigo Unico que genera alipos, de la siguiente manera: 
(Ejemplo, 04-2024-489 Donde 04: Mes Tributario, 2024: Año Fiscal, 489: Correlativo de la factura)
*DTE_TIPO_OPERACION --> Hace referencia a los codigos que maneja hacienda para identificar la naturaleza de operacion de la compra, por ej (1: GRAVADA, 2: NO GRAVADA, 3: EXCLUIDO O NO CONSTITUYE RENTA, 0: PERIODOS TRIBUTARIOS ANTERIORES A FEBRERO DE 2024, 9: EXCEPCIONES, OPERACIONES NO DEDUCIBLES PARA RENTA, ENTRE OTROS)
*DTE_CLASIFICACION --> Similar al anterior, aqui clasifica que naturaleza clasificacion pertenece a la compra, 
(por ej. 01: COSTO, 02: GASTO, 0: PERIODOS TRIBUTARIOS ANTERIORES A FEBRERO DE 2024, 09: EXCEPCIONES, OPERACIONES NO DEDUCIBLES PARA RENTA, ENTRE OTROS)
*DTE_SECTOR --> Similar a enteriores, mira la naturaleza del sector de la empresa/compra que realizo, 
(por ej. 1: INDUSTRIA, 2: COMERCIO, 3: AGROPECUARIA, 4: SERVICIOS, PROFESIONES, ARTES Y OFICIOS, 0: PERIODOS TRIBUTARIOS ANTERIORES A FEBRERO DE 2024, 09: EXCEPCIONES, OPERACIONES NO DEDUCIBLES PARA RENTA, ENTRE OTROS)
*DETE_TIPO_COSTO_GASTO --> Similar a anteriores, mira la naturaleza del Costo/Gasto en la compra,
(Por ej. 01: GASTOS DE VENTA SIN DONACIÓN, 02: GASTOS DE ADMINISTRACIÓN SIN DONACIÓN, 03: GASTOS FINANCIEROS SIN DONACIÓN, 04: COSTO ARTÍCULOS PRODUCIDOS/COMPRADOS IMPORTACIONES/INTERNACIONES, 05: COSTO ARTÍCULOS PRODUCIDOS/COMPRADOS INTERNO, 06: COSTOS INDIRECTOS DE FABRICACIÓN, 07: MANO DE OBRA, 0: PERIODOS TRIBUTARIOS ANTERIORES A FEBRERO DE 2024, 
09: EXCEPCIONES, OPERACIONES NO DEDUCIBLES PARA RENTA, ENTRE OTROS)
*TIPO_ACTIVO --> Hace Referencia a que Tipo de activo es, (Por ej. EDIFICACIONES, MAQUINARIA, VEHICULOS, OTROS BIENES MUEBLES)
*PORCENTAJE --> Es el porcentaje que se depreciara el Activo (Por ej. 5%, 20%, 25% y 50% respectivamente)
*VIDA_UTIL --> Es la vida util que suelen tener los Activos antes de depreciarce por completo (Por ej. 20, 4, 3 y 2 respectivamente)
*TIPO_DEPRECIACION --> Es el id del Activo al que se hace referencia, (Por ej. 01: EDIFICACIONES, 02: MAQUINARIA, 
03: Vehiculos y 04: OTROS BIENES MUEBLES)
*FECHA_DEPRECIACION --> Es la fecha en la que se comenzara a depreciar el Activo (La misma fecha que la compra)
*PRORRATEO --> Verifica si la compra es apta para prorratearse (01: Apto, 02: No Apto)
*PROCESADO_PRORRATEO --> Id que identifica que proceso de Prorrateo es
*PROCESADO_PRORRATEO_HECHO --> Este valida y verifica si el proceso del prorrateo se completo o no, siendo (01: Si, 02: No)
*COMPRA_ORIGINAL --> Hace referencia al id o correlativo de la compra Original en la que se inicio el proceso de prorrateo
