"""
Visualization module for displaying shuffle results and distributions.
"""

import os
from typing import List, Optional

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files
import matplotlib.pyplot as plt
import numpy as np

from .config import Config
from .models.deck import Deck
from .models.shuffle_cut import ShuffleCut
from .simulator import ShuffleResult


class Visualizer:
    """
    Visualizer for shuffle simulation results.
    
    Provides methods to visualize:
    - Single deck before and after shuffle
    - Cut distribution as histogram
    - Combined visualizations
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the visualizer.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config.default()
        self.fig_width = 10
        self.fig_height = 6
    
    def visualize_deck(self, deck: Deck, title: str = "Deck") -> plt.Figure:
        """
        Create a visualization of a single deck.
        
        Shows all 52 cards in a grid format.
        
        Args:
            deck: Deck to visualize
            title: Title for the plot
            
        Returns:
            matplotlib Figure object
        """
        fig, axes = plt.subplots(4, 13, figsize=(self.fig_width, 4))
        
        # Flatten axes for easier iteration
        axes_flat = axes.flatten()
        
        # Color mapping for suits
        suit_colors = {
            "clubs": "black",
            "diamonds": "red",
            "hearts": "red",
            "spades": "black"
        }
        
        # Plot each card
        for i, card in enumerate(deck.cards):
            ax = axes_flat[i]
            ax.text(0.5, 0.5, str(card), 
                   ha='center', va='center',
                   fontsize=12,
                   color=suit_colors.get(card.suit, 'black'),
                   fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(f"{i+1}", fontsize=8, fontweight='bold')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def visualize_cut_distribution(self, cuts: List[ShuffleCut], 
                                   title: str = "Cut Distribution") -> plt.Figure:
        """
        Create a histogram of cut ratios.
        
        Args:
            cuts: List of ShuffleCut instances
            title: Title for the plot
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(self.fig_width, self.fig_height))
        
        # Extract cut ratios
        ratios = [cut.cut_ratio for cut in cuts]
        
        # Create histogram
        ax.hist(ratios, bins=self.config.histogram_bins, 
               edgecolor='black', alpha=0.7, color='steelblue')
        
        # Add ideal cut line
        ax.axvline(x=0.5, color='red', linestyle='--', linewidth=2,
                  label='Ideal (0.5)')
        
        # Add mean line
        mean_ratio = sum(ratios) / len(ratios)
        ax.axvline(x=mean_ratio, color='green', linestyle='-', linewidth=2,
                  label=f'Mean ({mean_ratio:.3f})')
        
        ax.set_xlabel('Cut Ratio (Left Half / Total)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def visualize_before_after(self, deck_before: Deck, deck_after: Deck,
                               cut_position: int,
                               title: str = "Before and After Shuffle") -> plt.Figure:
        """
        Create side-by-side visualization of deck before and after shuffle.
        
        Args:
            deck_before: Deck state before shuffle
            deck_after: Deck state after shuffle
            cut_position: Position where cut was made
            title: Title for the plot
            
        Returns:
            matplotlib Figure object
        """
        fig, axes = plt.subplots(2, 1, figsize=(self.fig_width, self.fig_height * 2))
        
        # Visualize before
        fig1 = self.visualize_deck(deck_before, "Before Shuffle")
        axes[0].set_title("Before Shuffle", fontsize=14, fontweight='bold')
        
        # Visualize after
        fig2 = self.visualize_deck(deck_after, "After Shuffle")
        axes[1].set_title(f"After Shuffle (cut at position {cut_position})", 
                         fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        return fig
    
    def visualize_combined(self, cuts: List[ShuffleCut], 
                          sample_result: Optional[ShuffleResult] = None,
                          title: str = "Shuffle Simulation Results") -> plt.Figure:
        """
        Create a combined visualization with histogram and optional sample.
        
        Args:
            cuts: List of ShuffleCut instances
            sample_result: Optional sample shuffle result to show
            title: Title for the plot
            
        Returns:
            matplotlib Figure object
        """
        fig, axes = plt.subplots(2, 1, figsize=(self.fig_width, self.fig_height * 2))
        
        # Top: Histogram of cut distribution
        ax_hist = axes[0]
        ratios = [cut.cut_ratio for cut in cuts]
        
        ax_hist.hist(ratios, bins=self.config.histogram_bins,
                    edgecolor='black', alpha=0.7, color='steelblue')
        
        ax_hist.axvline(x=0.5, color='red', linestyle='--', linewidth=2,
                       label='Ideal (0.5)')
        
        mean_ratio = sum(ratios) / len(ratios)
        ax_hist.axvline(x=mean_ratio, color='green', linestyle='-', linewidth=2,
                       label=f'Mean ({mean_ratio:.3f})')
        
        ax_hist.set_xlabel('Cut Ratio', fontsize=12)
        ax_hist.set_ylabel('Frequency', fontsize=12)
        ax_hist.set_title('Cut Distribution', fontsize=14, fontweight='bold')
        ax_hist.legend()
        ax_hist.grid(True, alpha=0.3)
        
        # Bottom: Sample deck visualization if provided
        if sample_result:
            ax_sample = axes[1]
            
            # Show a simple representation of before and after
            before_str = " ".join([c.suit[0].upper() for c in sample_result.deck_before.cards[:10]])
            after_str = " ".join([c.suit[0].upper() for c in sample_result.deck_after.cards[:10]])
            
            ax_sample.text(0.1, 0.8, f"Before: {before_str}...", 
                          fontsize=10, va='top')
            ax_sample.text(0.1, 0.5, f"After: {after_str}...", 
                          fontsize=10, va='top')
            ax_sample.text(0.1, 0.2, f"Cut position: {sample_result.cut.left_half_size}", 
                          fontsize=10, va='bottom')
            
            ax_sample.set_xlim(0, 1)
            ax_sample.set_ylim(0, 1)
            ax_sample.axis('off')
            ax_sample.set_title('Sample Shuffle (first 10 cards)', fontsize=14, fontweight='bold')
        else:
            axes[1].axis('off')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def save_figure(self, fig: plt.Figure, filename: str, 
                   dpi: int = 100) -> str:
        """
        Save a figure to a file.
        
        Args:
            fig: matplotlib Figure object
            filename: Output filename (will be saved to output_dir)
            dpi: Resolution in dots per inch
            
        Returns:
            Full path to saved file
        """
        # Create output directory if it doesn't exist
        output_dir = self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def visualize_and_save(self, cuts: List[ShuffleCut], 
                          sample_result: Optional[ShuffleResult] = None,
                          filename: str = "shuffle_results.png",
                          title: str = "Shuffle Simulation Results") -> str:
        """
        Create and save a combined visualization.
        
        Args:
            cuts: List of ShuffleCut instances
            sample_result: Optional sample shuffle result
            filename: Output filename
            title: Title for the plot
            
        Returns:
            Full path to saved file
        """
        fig = self.visualize_combined(cuts, sample_result, title)
        return self.save_figure(fig, filename)
