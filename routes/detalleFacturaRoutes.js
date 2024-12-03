const express = require('express');
const router = express.Router();
const detalleFacturaController = require('../controllers/detalleFacturaController');

// Obtener todos los detalles de las facturas
router.get('/', detalleFacturaController.getAllDetallesFactura);

// Obtener un detalle de factura por ID
router.get('/:id', detalleFacturaController.getDetalleFacturaById);

// Crear un nuevo detalle de factura
router.post('/', detalleFacturaController.createDetalleFactura);

// Actualizar un detalle de factura
router.put('/:id', detalleFacturaController.updateDetalleFactura);

// Eliminar un detalle de factura
router.delete('/:id', detalleFacturaController.deleteDetalleFactura);

module.exports = router;
