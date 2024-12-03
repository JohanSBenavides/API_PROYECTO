const express = require('express');
const router = express.Router();
const pagosController = require('../controllers/pagosController');

// Obtener todos los pagos
router.get('/', pagosController.getAllPagos);

// Obtener un pago por ID
router.get('/:id', pagosController.getPagoById);

// Crear un nuevo pago
router.post('/', pagosController.createPago);

// Actualizar un pago
router.put('/:id', pagosController.updatePago);

// Eliminar un pago
router.delete('/:id', pagosController.deletePago);

module.exports = router;
