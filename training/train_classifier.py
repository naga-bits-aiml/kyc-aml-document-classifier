"""Training skeleton for EfficientNetB0 classifier.

This is a minimal example showing how training could be organized.
It expects a folder structure like:
  dataset_root/<class_name>/*.png
"""
import os
import tensorflow as tf

def build_model(num_classes):
    base = tf.keras.applications.EfficientNetB0(
        include_top=False, weights='imagenet', input_shape=(224,224,3), pooling='avg')
    x = tf.keras.layers.Dropout(0.2)(base.output)
    out = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
    model = tf.keras.Model(inputs=base.input, outputs=out)
    return model

def train(dataset_dir, epochs=1, batch_size=16, model_out="training/model/efficientnet_model.h5"):
    datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255, validation_split=0.1)
    train_gen = datagen.flow_from_directory(dataset_dir, target_size=(224,224), batch_size=batch_size, subset='training')
    val_gen = datagen.flow_from_directory(dataset_dir, target_size=(224,224), batch_size=batch_size, subset='validation')
    num_classes = len(train_gen.class_indices)
    model = build_model(num_classes)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_gen, validation_data=val_gen, epochs=epochs)
    os.makedirs(os.path.dirname(model_out), exist_ok=True)
    model.save(model_out)
    print(f"Saved model to {model_out}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--data", "-d", default="dataset_generator/output_dataset", help="Dataset root")
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=16)
    args = p.parse_args()
    train(args.data, epochs=args.epochs, batch_size=args.batch_size)