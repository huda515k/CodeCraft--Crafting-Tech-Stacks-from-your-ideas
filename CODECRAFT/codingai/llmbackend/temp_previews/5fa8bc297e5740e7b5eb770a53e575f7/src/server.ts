import express from 'express';
import { validateMiddleware, apiErrorHandler, genericErrorHandler } from './middleware/errorMiddleware';

const app = express();
app.use(express.json());

// Your routes here

// Middleware to handle validation errors
app.use(validateMiddleware);

// Middleware to handle custom API errors
app.use(apiErrorHandler);

// Middleware to handle all other errors
app.use(genericErrorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});