"""Standalone accuracy metrics for NexAI v_sandbox (no demo_engine imports)."""
import numpy as np


def replace_negatives(mat1, mat2):
    mat2_fixed = mat2.copy()
    mask = mat2_fixed == -1
    mat2_fixed[mask] = 1 - mat1[mask]
    return mat2_fixed


def accuracy(origin_mat, discovered):
    discovered = replace_negatives(origin_mat, discovered)
    diff = np.abs(origin_mat - discovered)
    score = np.sum(diff) / 100.0
    return 1 - score


def move_accuracy(steps_taken, max_steps=450):
    return 1 - (steps_taken / max_steps)


def absolute_accuracy(origin_mat, discovered, steps_taken, max_steps=450, x=7, y=3):
    base_accuracy = accuracy(origin_mat, discovered)
    step_score = move_accuracy(steps_taken, max_steps)
    return (x * base_accuracy + y * step_score) / (x + y)
