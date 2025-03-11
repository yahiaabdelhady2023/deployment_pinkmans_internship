# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import Sequential, load_model
# from tensorflow.keras.layers import SimpleRNN, Dense
# import os
# import datetime

# MODEL_PATH = "app/rnn_model.h5"
# def ensure_model_exists():
#     if not os.path.exists(MODEL_PATH):
#         print("Model not found. Training the model...")
#         train_and_save_model()
#     else:
#         print("Model already exists.")

# def create_rnn_model(input_shape):
#     model = Sequential([
#         SimpleRNN(50, return_sequences=True, input_shape=input_shape),
#         SimpleRNN(50),
#         Dense(1)
#     ])
#     model.compile(optimizer='adam', loss='mean_squared_error')
#     return model

# def train_and_save_model():
#     # Example data (replace with your actual data loading logic)
#     data = np.random.rand(100, 10, 1)  # 100 samples, 10 time steps, 1 feature
#     targets = np.random.rand(100, 1)   # 100 samples, 1 output

#     # Create and train the model
#     model = create_rnn_model((10, 1))
#     model.fit(data, targets, epochs=10, batch_size=32)

#     # Save the model
#     model.save(MODEL_PATH)
#     print("Model trained and saved.")
#     print("Model has been updated")

# def load_saved_model():
#     if os.path.exists(MODEL_PATH):
#         return load_model(MODEL_PATH)
#     else:
#         raise FileNotFoundError("Model not found. Train the model first.")

# def predict_new_data(model, new_data):
#     # Generate predictions
#     predictions = model.predict(new_data)

#     # Simulate upper future sales (replace with your actual logic)
#     upper_future_sales = predictions * 1.2  # Example: 20% higher than expected

#     # Format predictions into the desired structure
#     branches = ["Branch A", "Branch B", "Branch C"]
#     items = ["Item 1", "Item 2"]

#     predictions_branches = {}
#     for branch in branches:
#         predictions_branches[branch] = []
#         for i, item in enumerate(items):
#             # Handle cases where predictions has only one sample
#             if predictions.shape[0] == 1:
#                 pred_value = float(predictions[0][0])  # Use the first (and only) prediction
#                 upper_value = float(upper_future_sales[0][0])
#             else:
#                 pred_value = float(predictions[i][0])  # Use the i-th prediction
#                 upper_value = float(upper_future_sales[i][0])

#             predictions_branches[branch].append({
#                 "Item": item,
#                 "Expected Future Sales": pred_value,
#                 "Upper Future Sales": upper_value
#             })

#     return predictions_branches