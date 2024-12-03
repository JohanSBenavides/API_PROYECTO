const express = require('express');
const router = express.Router();
const categoriaController = require('../controllers/categoriaController');

// Obtener todas las categorías
router.get('/', categoriaController.getAllCategorias);

// Obtener una categoría por ID
router.get('/:id', categoriaController.getCategoriaById);

// Crear una nueva categoría
router.post('/', categoriaController.createCategoria);

// Actualizar una categoría
router.put('/:id', categoriaController.updateCategoria);

// Eliminar una categoría
router.delete('/:id', categoriaController.deleteCategoria);

module.exports = router;
