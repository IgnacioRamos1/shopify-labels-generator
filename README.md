
# Shopify Lambda

Create CSV for Correo Argentino containing the orders for all the Shopify Stores

## Workflow Diagram

<p><a target="_blank" href="https://app.eraser.io/workspace/ZBk8qkWx9FUNUjj43sqO" id="edit-in-eraser-github-link"><img alt="Edit in Eraser" src="https://firebasestorage.googleapis.com/v0/b/second-petal-295822.appspot.com/o/images%2Fgithub%2FOpen%20in%20Eraser.svg?alt=media&amp;token=968381c8-a7e7-472a-8ed6-4a6626da5501"></a></p>


### Add new Store

1. Agregar el campo de Compania en la pagina
2. Modificar el placeholder del checkout
 Company label = Calle
 Address1 label = Número
 Optional address2 label = Piso y departamento (Ej: “2A”)
3. Modificar en la pagina de configuracion de checkout:
   3.1 Hacer que en la parte superior de la pagina solo se pueda ingresar el e-mail
   3.2 Agregar como obligatorio un telefono celular al final del checkout
5. Agregar la api a la tienda y obtener el token
 Otorgar permisos de Read Orders
6. Agregar credenciales a los Secrets de AWS
7. Obtener el ID del grupo de wpp
8. Crear JSON con el nombre de la tienda que colocaste en AWS + _products
9. Deployear cambios a PROD y DEV\
      `sls deploy --stage prod`\
      `sls deploy --stage prod`
