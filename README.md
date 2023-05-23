# test_api
Este es un modelo basado en una API real, donde todas las rutas menos una fueron excluídas. 

La API permite interactuar con el recurso 'talents' de una base de datos en MongoDB. A su vez, esta ruta está integrada con un servicio externo de Thinkific (https://developers.thinkific.com/api/api-documentation/)

En este ejemplo, hay un elemento a corregir en la integración entre la API y Thinkific. Si bien los cambios podrían realizarse y funcionar correctamente, dada la necesidad de mantener sincronizadas las bases de datos de thinkific y MongoDB, es necesario añadir algunas reglas que asegurarían esta sincronización. 

