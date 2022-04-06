import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, render_template, request

from mnist_inference import inference

# webapp
app = Flask(__name__)

@app.route('/api/mnist', methods=['POST'])
def mnist():
    input = ((255 - np.array(request.json, dtype=np.uint8)) / 255.0).reshape(1, 784)
    # output1 = regression(input)
    output2 = inference(input)
    return jsonify(results=[output2, output2])

@app.route('/')
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9003)
