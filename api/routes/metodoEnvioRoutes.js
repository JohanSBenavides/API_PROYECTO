const express = require('express');
const router = express.Router();
const metodoEnvioController = require('../controllers/metodoEnvioController');

// Obtener todos los métodos de envío
router.get('/', metodoEnvioController.getAllMetodosEnvio);

// Obtener un método de envío por ID
router.get('/:id', metodoEnvioController.getMetodoEnvioById);

// Crear un nuevo método de envío
router.post('/', metodoEnvioController.createMetodoEnvio);

// Actualizar un método de envío
router.put('/:id', metodoEnvioController.updateMetodoEnvio);

// Eliminar un método de envío
router.delete('/:id', metodoEnvioController.deleteMetodoEnvio);

module.exports = router;
