import torch
import numpy as np
import cv2

import random


def circle_edging_mask(h, w, latent_ratio, add=2):

    # Use ratio for latent mask
    latent_h, latent_w = h // latent_ratio, w // latent_ratio


    center = (int(h / 2), int(w / 2))
    latent_center = (int(latent_h / 2), int(latent_w / 2))

    # use the smallest distance between the center and image walls
    radius = min(center[0], center[1], w - center[0], h - center[1])
    latent_radius = min(latent_center[0], latent_center[1], latent_h - latent_center[0],
                        latent_w - latent_center[1])

    # Define grid for image and latent image
    Y, X = np.ogrid[:h, :w]
    latent_Y, latent_X = np.ogrid[:latent_h, :latent_w]
    # Calculate distance from center
    dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
    latent_dist_from_center = np.sqrt((latent_X - latent_center[0]) ** 2 + (latent_Y - latent_center[1]) ** 2)
    # Define which fields have to be masked
    mask = dist_from_center <= radius
    latent_mask = latent_dist_from_center <= latent_radius

    mask, latent_mask = (mask == False) * add, (latent_mask == False) * add
    mask, latent_mask = torch.from_numpy(mask), torch.from_numpy(latent_mask)

    return mask, latent_mask


def rectangle_edging_mask(mask, latent_ratio, add=2):
    # Define how many pixels should be white for a strip
    height_up = 50
    height_down = 50
    width_left = 50
    width_right = 50
    # Parameter which define bounds by what percentage is deviation from the correponding above parameter
    l_s_b = (20, 50)
    r_s_b = (20, 50)
    u_s_b = (20, 50)
    d_s_b = (20, 50)
    # Define mask parameters
    height, width = mask.shape
    height_latent, width_latent = height // latent_ratio, width // latent_ratio
    # Initialize latent mask
    latent_mask = torch.zeros((height_latent, width_latent))

    for y in range(height):
        # Randomly get deviation from width_left
        spread_width_left = int(width_left * random.randint(l_s_b[0], l_s_b[1]) / 100)
        # Randomly choose the amount of pixels inside width_left bounds
        white_line_left = random.randint(width_left - spread_width_left, width_left + spread_width_left)
        # Randomly get deviation from width_right
        spread_width_right = int(width_right * random.randint(r_s_b[0], r_s_b[1]) / 100)
        # Randomly choose the amount of pixels inside width_right bounds
        white_line_right = random.randint(width_right - spread_width_right, width_right + spread_width_right)
        # Add values to the chosen pixels
        mask[y, 0:white_line_left] += add
        mask[y, width - white_line_right:] += add
        # Scale results for latent_mask
        if (y + 1) % latent_ratio == 0:
            y_latent = (y + 1) // latent_ratio - 1
            white_line_left_latents = white_line_left // latent_ratio
            white_line_right_latents = white_line_right // latent_ratio

            latent_mask[y_latent, 0:white_line_left_latents] += add
            latent_mask[y_latent, width_latent - white_line_right_latents:] += add

    for x in range(width):
        # Randomly get deviation from height_up
        spread_height_up = int(height_up * random.randint(u_s_b[0], u_s_b[1]) / 100)
        # Randomly choose the amount of pixels inside height_up bounds
        white_line_up = random.randint(height_up - spread_height_up, height_up + spread_height_up)
        # Randomly get deviation from height_down
        spread_height_down = int(height_down * random.randint(d_s_b[0], d_s_b[1]) / 100)
        # Randomly choose the amount of pixels inside height_down bounds
        white_line_down = random.randint(height_down - spread_height_down, height_down + spread_height_down)
        # Add values to the chosen pixels
        mask[0:white_line_up, x] += add
        mask[height - white_line_down:, x] += add
        # Scale results for latent_mask
        if (x + 1) % latent_ratio == 0:
            x_latent = (x + 1) // latent_ratio - 1
            white_line_down_latents = white_line_down // latent_ratio
            white_line_up_latents = white_line_up // latent_ratio

            latent_mask[0:white_line_up_latents, x_latent] += add
            latent_mask[height_latent - white_line_down_latents:, x_latent] += add

    return mask, latent_mask


def random_mask(images, height, width, torch_device, latent_ratio, add=2):
    # Define how far in percentages to lower the curtain as a random mask
    c = 0.35
    # Define interpolation type
    interpolation = cv2.INTER_NEAREST
    # Define parameters masks according to the above settings
    np.random.seed(123)
    latent_height, latent_width = height // latent_ratio, width // latent_ratio
    scaled_height = int(c * height)
    scaled_latent_height = int(c * latent_height)

    # Create random mask
    mask = np.random.randint(0, 2, size=(scaled_height, width), dtype=np.uint8) * add
    # Resize mask to get latent mask
    noised_latent_mask_wt_reshape = cv2.resize(mask, dsize=(scaled_latent_height, latent_width),
                                               interpolation=interpolation)
    # Apply reshape for the mask
    noised_latent_mask = noised_latent_mask_wt_reshape.reshape(scaled_latent_height, latent_width)
    # Create fill_ones to apply it to the fields that have to be white
    fill_ones = torch.ones(3).to(torch_device).view(3, 1, 1)
    mask = torch.from_numpy(mask).to(torch_device)
    # Extract part with random noise and without
    noised_part, common_part = images[:, :, :scaled_height, :], images[:, :, scaled_height:, :]
    # Apply fill_ones where there is noise (fields that have to be white)
    noised_result = torch.where(mask[None, :, :] > 1, fill_ones, noised_part)
    # Concatenate results
    result = torch.cat((noised_result, common_part), 2)
    # Calculate the error
    error = torch.abs(images - result).mean()
    # Make the same for the latent_mask
    common_latent_part = np.zeros((latent_height - scaled_latent_height, latent_width))
    latent_mask = np.concatenate((noised_latent_mask, common_latent_part), axis=0)
    latent_mask = torch.from_numpy(latent_mask).to(torch_device).to(torch.float16)

    return error, latent_mask