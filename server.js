const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
const routes = require('./routes/index');

// Configuración del middleware
app.use(cors());
app.use(bodyParser.json());

// Uso de las rutas
app.use('/api', routes);

// Configurar el puerto
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en el puerto ${PORT}`);
});
