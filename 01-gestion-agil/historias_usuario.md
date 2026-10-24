# Historias de usuario: Petstore QA

## HU-01: Registrar mascota

**Como** empleado de la tienda,
**quiero** registrar una mascota con nombre y estado,
**para** que esté disponible en el catálogo.

### Criterios de aceptación

- **CA-01.1** Dado que envío un nombre y el estado "available", cuando registro la mascota, entonces el sistema responde con éxito y devuelve la mascota con su id.
- **CA-01.2** Dado que envío un estado distinto de "available", "pending" o "sold", cuando registro la mascota, entonces el sistema rechaza la solicitud.
- **CA-01.3** Dado que no envío el nombre, cuando registro la mascota, entonces el sistema rechaza la solicitud.

## HU-02: Consultar mascota por id

**Como** empleado de la tienda,
**quiero** consultar una mascota por su id,
**para** informar al cliente sus datos y su disponibilidad.

### Criterios de aceptación

- **CA-02.1** Dado que consulto un id que existe, cuando envío la consulta, entonces el sistema responde con éxito (código 200) y devuelve los datos de esa mascota.
- **CA-02.2** Dado que consulto un id con formato válido que no existe, cuando envío la consulta, entonces el sistema responde que la mascota no fue encontrada (código 404).
- **CA-02.3** Dado que consulto un id con formato inválido (por ejemplo, letras), cuando envío la consulta, entonces el sistema rechaza la solicitud (código 400).

## HU-03: Buscar mascotas por estado

**Como** empleado de la tienda,
**quiero** buscar las mascotas según su estado,
**para** mostrarles a los clientes las mascotas que pueden adquirir.

### Criterios de aceptación

- **CA-03.1** Dado que busco mascotas con el estado "sold", cuando envío la consulta, entonces el sistema responde con éxito (código 200) y todas las mascotas devueltas tienen el estado "sold".
- **CA-03.2** Dado que busco con un estado distinto de "available", "pending" o "sold", cuando envío la consulta, entonces el sistema rechaza la solicitud (código 400).
