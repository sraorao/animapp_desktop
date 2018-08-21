library(data.table)
library(tidyverse)

# cold = 19oC, room = 37oC

# read CSV files ----
cold_files <- list.files("19oC/", pattern = "processed.csv$", full.names = TRUE)
room_files <- list.files("37oC/", pattern = "processed.csv$", full.names = TRUE)

cold <- lapply(cold_files, fread)
room <- lapply(room_files, fread)
room <- room[-c(1, 3, 5, 15)]

sapply(cold, nrow)
sapply(room, nrow)

cold_dist <- sapply(cold, function(x) sum(x[, 4]))
room_dist <- sapply(room, function(x) sum(x[, 4]))

length(cold_dist) 
length(room_dist)
room_dist <- c(room_dist, NA, NA, NA, NA)
distances_df <- data.frame(cold = cold_dist, room = room_dist)
#distances_df <- distances_df[-c(1, 3, 5, 15), ]
# t test ----
with(distances_df, t.test(cold, room))

# distances boxplot ----
distances_df %>%
  gather(key = "sample_name", value = "distance") %>%
  ggplot(aes(x = sample_name, y = distance)) + 
  geom_boxplot() + 
  geom_point() + 
  theme_bw() + 
  scale_y_continuous(limits = c(0, 500)) -> p
p
#plotly::ggplotly(p)

# individual paths ----
lapply(cold, function(x){
  ggplot(x, aes(x = V1, y = V2)) + 
    geom_point() + 
    theme_bw() + 
    scale_x_continuous(limits = c(0, 640)) + 
    scale_y_continuous(limits = c(0, 480)) 
})

lapply(room, function(x){
  ggplot(x, aes(x = V1, y = V2)) + 
    geom_point() + 
    theme_bw() + 
    scale_x_continuous(limits = c(0, 640)) + 
    scale_y_continuous(limits = c(0, 480)) 
})



# normalise starting point to centre ----
cold_norm <- lapply(cold, function(x){
  startx = x$V1[1]
  starty = x$V2[1]
  x = x[1:900, ]
  x$V1 <- x$V1 - startx + 320
  x$V2 <- x$V2 - starty + 240
  return(x)
})

lapply(cold_norm, nrow)
cold_combined <- do.call(rbind, lapply(1:length(cold_norm), function(x) data.table(cold_norm[[x]])[,sample_name:=paste0("cold_", x)])) 

room_norm <- lapply(room, function(x){
  startx = x$V1[1]
  starty = x$V2[1]
  x = x[1:900, ]
  x$V1 <- x$V1 - startx + 320
  x$V2 <- x$V2 - starty + 240
  return(x)
})

lapply(room_norm, nrow)

room_combined <- do.call(rbind, lapply(1:length(room_norm), function(x) data.table(room_norm[[x]])[,sample_name:=paste0("room_", x)])) 

combined <- list(room_combined, cold_combined)

# normalised paths all in one plot ----
do.call(rbind, combined) %>%
  mutate(genotype = sub("_[0-9]{1,2}", "", sample_name)) %>% #filter(genotype == "room") %>%
  ggplot(aes(x = V1, y = V2, colour = genotype)) + 
  #scale_colour_manual(values = c("dodgerblue1", "salmon")) +
  geom_path(aes(group = sample_name), alpha = 0.5, size = 3) + 
  geom_path(aes(colour = sample_name, group = sample_name), alpha = 1, size = 0.5) + 
  theme_bw() + 
  scale_x_continuous(limits = c(0, 640)) + 
  scale_y_continuous(limits = c(0, 480)) -> p
p
#plotly::ggplotly(p)
circleFun <- function(center = c(0,0),diameter = 1, npoints = 100){
  r = diameter / 2
  tt <- seq(0,2*pi,length.out = npoints)
  xx <- center[1] + r * cos(tt)
  yy <- center[2] + r * sin(tt)
  return(data.frame(x = xx, y = yy))
}
circ1 <- circleFun(center = c(320, 240), diameter = 50, npoints = 100)
circ2 <- circleFun(center = c(320, 240), diameter = 100, npoints = 100)
circ3 <- circleFun(center = c(320, 240), diameter = 200, npoints = 100)
circ4 <- circleFun(center = c(320, 240), diameter = 300, npoints = 100)
circ5 <- circleFun(center = c(320, 240), diameter = 450, npoints = 100)

centre_df <- data.frame(x = c(320, rep(NA, 26999)), y = c(240, rep(NA, 26999)))


p + geom_point(data = centre_df, mapping = aes(x = x, y = y), colour = "black", size = 5, alpha = 0.3) + 
  geom_path(mapping = aes(x, y), data = circ1, colour = "lightblue") +
  geom_path(mapping = aes(x, y), data = circ2, colour = "blue", alpha = 0.25) +
  geom_path(mapping = aes(x, y), data = circ3, colour = "darkblue", alpha = 0.25) +
  geom_path(mapping = aes(x, y), data = circ4, colour = "black", alpha = 0.25) +
  geom_path(mapping = aes(x, y), data = circ5, colour = "black", alpha = 0.25) +
  theme_void() +
  guides(colour = guide_legend(override.aes = list(alpha = 1))) -> q
q
#plotly::ggplotly(q)
