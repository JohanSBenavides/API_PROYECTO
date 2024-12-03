const express = require('express');
const router = express.Router();

const carritoRoutes = require('./carritoRoutes');
const categoriaRoutes = require('./categoriaRoutes');
const comprasRoutes = require('./comprasRoutes');
const detalleCarritoRoutes = require('./detalleCarritoRoutes');
const detalleFacturaRoutes = require('./detalleFacturaRoutes');
const metodoEnvioRoutes = require('./metodoEnvioRoutes');
const pagosRoutes = require('./pagosRoutes');
const productoRoutes = require('./productoRoutes');

// Asocia las rutas con el prefijo correspondiente
router.use('/carrito_compras', carritoRoutes);
router.use('/categoria', categoriaRoutes);
router.use('/compras', comprasRoutes);
router.use('/detalle_carrito', detalleCarritoRoutes);
router.use('/detalle_factura', detalleFacturaRoutes);
router.use('/metodo_envio', metodoEnvioRoutes);
router.use('/pagos', pagosRoutes);
router.use('/producto', productoRoutes);

module.exports = router;
