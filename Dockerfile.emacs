FROM gmoben/dev-env:minimal

ARG user

USER root

RUN cp /dotfiles/.config/systemd/user/emacs.service /usr/lib/systemd/system/emacs.service
RUN mkdir /dotfiles/.emacs.d/emms
# RUN ln -s /dotfiles/.emacs.conf /root/.emacs.conf
# RUN ln -s /dotfiles/.emacs.d /root/.emacs.d
# RUN systemctl enable emacs
# RUN emacs --daemon --eval "(kill-emacs)" || true

USER $user
RUN mkdir -p /home/$user/.config/systemd/user/
RUN ln -s /dotfiles/.config/systemd/user/emacs.service /home/$user/.config/systemd/user/emacs.service
RUN cp -R /dotfiles/.emacs.conf /home/$user/.emacs.conf
RUN cp -R /dotfiles/.emacs.d /home/$user/.emacs.d
RUN systemctl enable --user emacs
RUN emacs --daemon --eval "(kill-emacs)" || true
