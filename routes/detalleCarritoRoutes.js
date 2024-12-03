const express = require('express');
const router = express.Router();
const detalleCarritoController = require('../controllers/detalleCarritoController');

// Obtener todos los detalles del carrito
router.get('/', detalleCarritoController.getAllDetallesCarrito);

// Obtener un detalle del carrito por ID
router.get('/:id', detalleCarritoController.getDetalleCarritoById);

// Crear un nuevo detalle en el carrito
router.post('/', detalleCarritoController.createDetalleCarrito);

// Actualizar un detalle del carrito
router.put('/:id', detalleCarritoController.updateDetalleCarrito);

// Eliminar un detalle del carrito
router.delete('/:id', detalleCarritoController.deleteDetalleCarrito);

module.exports = router;
