const express = require('express');
const router = express.Router();
const comprasController = require('../controllers/comprasController');

// Obtener todas las compras
router.get('/', comprasController.getAllCompras);

// Obtener una compra por ID
router.get('/:id', comprasController.getCompraById);

// Crear una nueva compra
router.post('/', comprasController.createCompra);

// Actualizar una compra
router.put('/:id', comprasController.updateCompra);

// Eliminar una compra
router.delete('/:id', comprasController.deleteCompra);

module.exports = router;
