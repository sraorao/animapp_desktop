library(tidyverse)
library(cowplot)
library(data.table)

draw_dual_plot <- function(filename, save = TRUE) {
  
  fread(filename) %>%
    rowwise() %>%
    mutate(m = max(V6, V7)) %>%
    mutate(mi = min(V6, V7)) %>%
    mutate(r = mi/m) -> df
  
  df %>%
    ggplot(aes(x = V3, y = m)) + 
    geom_line(color = "salmon") +
    scale_y_continuous(limits = c(0, 20)) +
    theme_bw() -> p1
  
  df %>%
    ggplot(aes(x = V3, y = r)) + 
    geom_line() +
    scale_y_continuous(limits = c(0, 1)) +
    theme_bw() -> p2
  p <- plot_grid(p1, p2, nrow = 2, align = "v")
  if (save) {
    save_plot(paste0(filename, ".pdf"), p, base_height = 4, base_width = 8)
  }
  return(list(p1, p2))
}

process_files <- function(folder, save = TRUE, plotly = FALSE, dual = TRUE) {
  files <- list.files(path = folder, pattern = "mp4.csv$", full.names = TRUE)
  if (plotly) {
    lapply(files, function(x) plotly::ggplotly(draw_dual_plot(x, save = FALSE)[[1]]))
  } else {
    lapply(files, draw_dual_plot, save = save)
  }
  if (dual) {
    lapply(files, function(x) {
            plot_list <- draw_dual_plot(x, save = save)
            plot_grid(plot_list[[1]], plot_list[[2]], ncol = 1)
              }
          )
  }
}

process_files("19oC/", save = TRUE, plotly = FALSE, dual = TRUE)
process_files("37oC/", save = FALSE, plotly = FALSE, dual = TRUE)
