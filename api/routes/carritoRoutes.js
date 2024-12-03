const express = require('express');
const router = express.Router();
const carritoController = require('../controllers/carritoController');

// Obtener todos los carritos
router.get('/', carritoController.getAllCarritos);

// Obtener un carrito por ID
router.get('/:id', carritoController.getCarritoById);

// Crear un nuevo carrito
router.post('/', carritoController.createCarrito);

// Actualizar un carrito
router.put('/:id', carritoController.updateCarrito);

// Eliminar un carrito
router.delete('/:id', carritoController.deleteCarrito);

module.exports = router;
